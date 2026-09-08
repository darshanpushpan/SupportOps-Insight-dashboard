"""SupportOps Insight - Main Flask application."""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from config import config_by_name
from utils.incident_generator import IncidentGenerator
from utils.log_parser import LogParser
from utils.markdown_lite import render_markdown
from utils.ops_signals import app_signals, auth_signals, recommended_actions
from utils.severity_classifier import SeverityClassifier
from utils.ticket_store import (
    bar_rows,
    compute_ticket_metrics,
    filter_tickets,
    get_ticket,
    load_tickets,
    unique_values,
)

# In-memory storage for parsed logs
uploaded_files: Dict[str, Dict[str, Any]] = {}


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Application factory for SupportOps Insight.

    Args:
        config_name: Configuration environment name.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    env = config_name or os.environ.get('FLASK_ENV', 'development')
    config_class = config_by_name.get(env, config_by_name['default'])
    app.config.from_object(config_class)

    _ensure_directories(app)
    _setup_logging(app)

    log_parser = LogParser()
    classifier = SeverityClassifier(
        severity_weights=app.config['SEVERITY_WEIGHTS'],
        critical_keywords=app.config['CRITICAL_KEYWORDS'],
        critical_services=app.config['CRITICAL_SERVICES'],
    )
    incident_generator = IncidentGenerator(classifier)

    register_routes(app, log_parser, classifier, incident_generator)
    register_error_handlers(app)

    return app


def _ensure_directories(app: Flask) -> None:
    """Create required directories if they do not exist."""
    for folder_key in ('UPLOAD_FOLDER', 'REPORTS_FOLDER', 'LOGS_FOLDER'):
        path = app.config[folder_key]
        os.makedirs(path, exist_ok=True)


def _setup_logging(app: Flask) -> None:
    """Configure application logging to file."""
    log_file = os.path.join(app.config['LOGS_FOLDER'], 'supportops.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
    )


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check whether a filename has an allowed extension."""
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    )


def get_dashboard_stats() -> Dict[str, Any]:
    """Compute dashboard statistics from in-memory storage."""
    total_logs = sum(len(item['logs']) for item in uploaded_files.values())
    files_count = len(uploaded_files)
    error_count = 0
    services = set()

    for item in uploaded_files.values():
        for log in item['logs']:
            level = str(log.get('level', '')).upper()
            if level in {'ERROR', 'CRITICAL'}:
                error_count += 1
            services.add(log.get('service', 'Unknown'))

    return {
        'total_logs': total_logs,
        'files_uploaded': files_count,
        'error_count': error_count,
        'services_affected': len(services),
    }


def filter_logs(
    logs: List[Dict[str, Any]],
    level: str = '',
    service: str = '',
    search: str = '',
    sort_by: str = 'timestamp',
    sort_order: str = 'desc',
) -> List[Dict[str, Any]]:
    """
    Filter and sort log entries based on query parameters.

    Args:
        logs: Source log entries.
        level: Severity level filter.
        service: Service name filter.
        search: Keyword search string.
        sort_by: Sort field (timestamp or level).
        sort_order: asc or desc.

    Returns:
        Filtered and sorted log list.
    """
    filtered = logs

    if level:
        filtered = [
            log for log in filtered
            if str(log.get('level', '')).upper() == level.upper()
        ]

    if service:
        filtered = [
            log for log in filtered
            if log.get('service', '') == service
        ]

    if search:
        search_lower = search.lower()
        filtered = [
            log for log in filtered
            if search_lower in str(log.get('message', '')).lower()
            or search_lower in str(log.get('service', '')).lower()
            or search_lower in str(log.get('host', '')).lower()
        ]

    reverse = sort_order.lower() != 'asc'

    if sort_by == 'level':
        level_order = {'DEBUG': 1, 'INFO': 2, 'WARNING': 3, 'ERROR': 4, 'CRITICAL': 5}
        filtered.sort(
            key=lambda log: level_order.get(str(log.get('level', 'INFO')).upper(), 0),
            reverse=reverse,
        )
    else:
        filtered.sort(
            key=lambda log: str(log.get('parsed_timestamp') or log.get('timestamp') or ''),
            reverse=reverse,
        )

    return filtered


def register_routes(
    app: Flask,
    log_parser: LogParser,
    classifier: SeverityClassifier,
    incident_generator: IncidentGenerator,
) -> None:
    """Register all application routes."""

    @app.route('/')
    def index():
        """Dashboard home page with log and ticket statistics."""
        stats = get_dashboard_stats()
        tickets = load_tickets()
        ticket_metrics = compute_ticket_metrics(tickets)
        auth = auth_signals()
        app_health = app_signals()
        return render_template(
            'index.html',
            stats=stats,
            ticket_metrics=ticket_metrics,
            auth=auth,
            app_health=app_health,
            insights=recommended_actions(auth, app_health),
            status_bars=bar_rows(ticket_metrics['by_status'], ['Open', 'In Progress', 'Escalated', 'Resolved', 'Closed']),
            priority_bars=bar_rows(ticket_metrics['by_priority'], ['P1', 'P2', 'P3', 'P4']),
            sla_bars=bar_rows(ticket_metrics['by_sla'], ['Met', 'At Risk', 'Breached']),
            category_bars=bar_rows(ticket_metrics['by_category']),
            simulated=True,
        )

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        """File upload form and processing."""
        if request.method == 'POST':
            files = request.files.getlist('files')
            if not files or all(not f.filename for f in files):
                flash('Please select at least one file to upload.', 'error')
                return redirect(url_for('upload'))

            uploaded_count = 0
            for file_storage in files:
                if not file_storage.filename:
                    continue

                filename = secure_filename(file_storage.filename)
                if not allowed_file(filename, app.config['ALLOWED_EXTENSIONS']):
                    flash(
                        f'Invalid file type: {filename}. '
                        f'Allowed: {", ".join(app.config["ALLOWED_EXTENSIONS"])}',
                        'error',
                    )
                    continue

                file_id = str(uuid.uuid4())[:8]
                stored_name = f'{file_id}_{filename}'
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)

                try:
                    file_storage.save(file_path)
                    logs = log_parser.parse_file(file_path)

                    uploaded_files[file_id] = {
                        'file_id': file_id,
                        'filename': filename,
                        'stored_name': stored_name,
                        'path': file_path,
                        'logs': logs,
                        'uploaded_at': datetime.now().isoformat(),
                        'format': log_parser.detect_format(
                            [log.get('raw', '') for log in logs[:20]]
                        ),
                    }
                    uploaded_count += 1
                    logging.info('Uploaded and parsed file: %s (%d entries)', filename, len(logs))
                except Exception as exc:
                    flash(f'Error processing {filename}: {exc}', 'error')
                    logging.exception('Upload error for %s', filename)

            if uploaded_count:
                flash(
                    f'Successfully uploaded and parsed {uploaded_count} file(s).',
                    'success',
                )
                if uploaded_count == 1:
                    latest_id = list(uploaded_files.keys())[-1]
                    return redirect(url_for('analyze_file', file_id=latest_id))

            return redirect(url_for('upload'))

        file_list = [
            {
                'file_id': item['file_id'],
                'filename': item['filename'],
                'uploaded_at': item['uploaded_at'],
                'log_count': len(item['logs']),
                'format': item.get('format', 'unknown'),
            }
            for item in uploaded_files.values()
        ]
        file_list.sort(key=lambda item: item['uploaded_at'], reverse=True)
        return render_template('upload.html', files=file_list)

    @app.route('/analyze')
    def analyze():
        """Redirect to most recent file analysis or upload page."""
        if not uploaded_files:
            flash('No log files uploaded yet. Please upload a file first.', 'info')
            return redirect(url_for('upload'))

        latest = max(uploaded_files.values(), key=lambda item: item['uploaded_at'])
        return redirect(url_for('analyze_file', file_id=latest['file_id']))

    @app.route('/analyze/<file_id>')
    def analyze_file(file_id: str):
        """Log analysis view with filters for a specific file."""
        file_data = uploaded_files.get(file_id)
        if not file_data:
            flash('Log file not found.', 'error')
            return redirect(url_for('upload'))

        level = request.args.get('level', '')
        service = request.args.get('service', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc')
        page = max(int(request.args.get('page', 1)), 1)
        per_page = int(request.args.get('per_page', 100))

        all_logs = file_data['logs']
        filtered_logs = filter_logs(all_logs, level, service, search, sort_by, sort_order)
        error_groups = classifier.group_errors(filtered_logs)

        services = sorted({log.get('service', 'Unknown') for log in all_logs})
        total_count = len(all_logs)
        filtered_count = len(filtered_logs)

        start = (page - 1) * per_page
        end = start + per_page
        paginated_logs = filtered_logs[start:end]
        total_pages = max((filtered_count + per_page - 1) // per_page, 1)

        return render_template(
            'analyze.html',
            file_id=file_id,
            filename=file_data['filename'],
            logs=paginated_logs,
            all_logs_count=total_count,
            filtered_count=filtered_count,
            error_groups=error_groups,
            services=services,
            filters={
                'level': level,
                'service': service,
                'search': search,
                'sort_by': sort_by,
                'sort_order': sort_order,
            },
            pagination={
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages,
            },
        )

    @app.route('/api/logs/<file_id>')
    def api_logs(file_id: str):
        """JSON API endpoint for log data."""
        file_data = uploaded_files.get(file_id)
        if not file_data:
            return jsonify({'error': 'File not found'}), 404

        level = request.args.get('level', '')
        service = request.args.get('service', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'desc')

        filtered_logs = filter_logs(
            file_data['logs'], level, service, search, sort_by, sort_order
        )
        error_groups = classifier.group_errors(filtered_logs)

        return jsonify({
            'file_id': file_id,
            'filename': file_data['filename'],
            'total_count': len(file_data['logs']),
            'filtered_count': len(filtered_logs),
            'logs': filtered_logs,
            'error_groups': error_groups,
        })

    @app.route('/incident/generate', methods=['GET', 'POST'])
    def incident_generate():
        """Incident report generation form and processing."""
        if request.method == 'POST':
            file_id = request.form.get('file_id', '')
            notes = request.form.get('notes', '')
            selected_ids = request.form.getlist('logs')
            report_scope = request.form.get('report_scope', 'selected')

            file_data = uploaded_files.get(file_id)
            if not file_data:
                flash('Log file not found.', 'error')
                return redirect(url_for('upload'))

            if report_scope == 'all_errors':
                report_logs = [
                    log for log in file_data['logs']
                    if str(log.get('level', '')).upper() in {'ERROR', 'CRITICAL', 'WARNING'}
                ]
            elif selected_ids:
                report_logs = [
                    log for log in file_data['logs']
                    if log.get('id') in selected_ids
                ]
            else:
                flash('Please select at least one log entry or choose "All Errors".', 'error')
                return redirect(url_for('analyze_file', file_id=file_id))

            if not report_logs:
                flash('No log entries available for the report.', 'error')
                return redirect(url_for('analyze_file', file_id=file_id))

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f'incident_{timestamp}.html'
            report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)

            error_groups = classifier.group_errors(report_logs)
            report_id = incident_generator.save_report(
                logs=report_logs,
                output_path=report_path,
                source_filename=file_data['filename'],
                notes=notes,
                error_groups=error_groups,
            )

            flash(f'Incident report {report_id} generated successfully.', 'success')
            return redirect(url_for('view_report', filename=report_filename))

        file_id = request.args.get('file_id', '')
        if file_id and file_id in uploaded_files:
            return redirect(url_for('analyze_file', file_id=file_id))

        if uploaded_files:
            latest = max(uploaded_files.values(), key=lambda item: item['uploaded_at'])
            return redirect(url_for('analyze_file', file_id=latest['file_id']))

        flash('No log files available. Upload logs first.', 'info')
        return redirect(url_for('upload'))

    @app.route('/reports')
    def reports_list():
        """List all generated incident reports."""
        reports = []
        reports_dir = app.config['REPORTS_FOLDER']

        for filename in os.listdir(reports_dir):
            if not filename.endswith('.html'):
                continue
            file_path = os.path.join(reports_dir, filename)
            stat = os.stat(file_path)
            reports.append({
                'filename': filename,
                'created_at': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': stat.st_size,
                'size_display': _format_file_size(stat.st_size),
            })

        reports.sort(key=lambda item: item['created_at'], reverse=True)
        return render_template('reports.html', reports=reports)

    @app.route('/reports/<filename>')
    def view_report(filename: str):
        """View a specific generated report."""
        safe_name = secure_filename(filename)
        report_path = os.path.join(app.config['REPORTS_FOLDER'], safe_name)

        if not os.path.exists(report_path):
            flash('Report not found.', 'error')
            return redirect(url_for('reports_list'))

        with open(report_path, 'r', encoding='utf-8') as handle:
            content = handle.read()

        return content, 200, {'Content-Type': 'text/html; charset=utf-8'}

    @app.route('/delete/<file_id>', methods=['POST'])
    def delete_file(file_id: str):
        """Delete an uploaded log file."""
        file_data = uploaded_files.get(file_id)
        if not file_data:
            flash('File not found.', 'error')
            return redirect(url_for('upload'))

        try:
            if os.path.exists(file_data['path']):
                os.remove(file_data['path'])
            del uploaded_files[file_id]
            flash(f'Deleted {file_data["filename"]}.', 'success')
            logging.info('Deleted file: %s', file_data['filename'])
        except OSError as exc:
            flash(f'Error deleting file: {exc}', 'error')

        return redirect(url_for('upload'))

    @app.route('/tickets')
    def tickets_list():
        """Simulated ticket queue with filters."""
        all_tickets = load_tickets()
        filters = {
            'status': request.args.get('status', ''),
            'priority': request.args.get('priority', ''),
            'category': request.args.get('category', ''),
            'environment': request.args.get('environment', ''),
            'assigned_group': request.args.get('assigned_group', ''),
            'sla_status': request.args.get('sla_status', ''),
            'date_from': request.args.get('date_from', ''),
            'date_to': request.args.get('date_to', ''),
        }
        filtered = filter_tickets(all_tickets, **filters)
        display_metrics = compute_ticket_metrics(filtered)
        return render_template(
            'tickets.html',
            tickets=filtered,
            filters=filters,
            metrics=display_metrics,
            statuses=unique_values(all_tickets, 'status'),
            priorities=['P1', 'P2', 'P3', 'P4'],
            categories=unique_values(all_tickets, 'category'),
            environments=unique_values(all_tickets, 'environment'),
            groups=unique_values(all_tickets, 'assigned_group'),
            sla_statuses=['Met', 'At Risk', 'Breached'],
            status_bars=bar_rows(display_metrics['by_status'], ['Open', 'In Progress', 'Escalated', 'Resolved', 'Closed']),
            priority_bars=bar_rows(display_metrics['by_priority'], ['P1', 'P2', 'P3', 'P4']),
            category_bars=bar_rows(display_metrics['by_category']),
            group_bars=bar_rows(display_metrics['by_group']),
            sla_bars=bar_rows(display_metrics['by_sla'], ['Met', 'At Risk', 'Breached']),
            total_unfiltered=len(all_tickets),
            simulated=True,
        )

    @app.route('/tickets/<ticket_id>')
    def ticket_detail(ticket_id: str):
        """Simulated ticket triage / detail view."""
        ticket = get_ticket(ticket_id)
        if not ticket:
            flash('Ticket not found in the simulated data set.', 'error')
            return redirect(url_for('tickets_list'))
        return render_template('ticket_detail.html', ticket=ticket, simulated=True)

    @app.route('/operations')
    def operations():
        """Authentication signals, application health, and support insights."""
        auth = auth_signals()
        health = app_signals()
        tickets = load_tickets()
        metrics = compute_ticket_metrics(tickets)
        return render_template(
            'operations.html',
            auth=auth,
            app_health=health,
            insights=recommended_actions(auth, health),
            metrics=metrics,
            recurring=metrics['recurring'],
            simulated=True,
        )

    @app.route('/knowledge')
    def knowledge():
        """Index of simulated runbooks and incident documents."""
        docs = [
            {'title': 'Incident summary', 'path': 'docs/incident-summary.md'},
            {'title': 'Root-cause analysis', 'path': 'docs/root-cause-analysis.md'},
            {'title': 'Incident communication templates', 'path': 'docs/incident-communication.md'},
            {'title': 'Support metrics (simulated)', 'path': 'reports/support-metrics.md'},
            {'title': 'Log analysis summary', 'path': 'reports/log-analysis-summary.md'},
            {'title': 'User Cannot Sign In', 'path': 'docs/runbooks/user-cannot-sign-in.md'},
            {'title': 'Account Lockout', 'path': 'docs/runbooks/account-lockout.md'},
            {'title': 'MFA Troubleshooting', 'path': 'docs/runbooks/mfa-troubleshooting.md'},
            {'title': 'Incident Escalation and Prioritization', 'path': 'docs/runbooks/incident-escalation.md'},
            {'title': 'Application Performance Triage', 'path': 'docs/runbooks/application-performance.md'},
            {'title': 'POS / Device Support Triage', 'path': 'docs/runbooks/pos-device-support.md'},
        ]
        return render_template('knowledge.html', docs=docs, simulated=True)

    @app.route('/knowledge/view')
    def knowledge_view():
        """Render a local Markdown document inside the dashboard."""
        relative = request.args.get('path', '')
        allowed_prefix = ('docs/', 'reports/')
        if not relative.startswith(allowed_prefix) or '..' in relative or relative.endswith('.html'):
            flash('That document is not available.', 'error')
            return redirect(url_for('knowledge'))

        full_path = os.path.normpath(os.path.join(app.config['BASE_DIR'], relative.replace('/', os.sep)))
        base_dir = os.path.normpath(app.config['BASE_DIR'])
        if not full_path.startswith(base_dir) or not os.path.isfile(full_path):
            flash('Document not found.', 'error')
            return redirect(url_for('knowledge'))

        with open(full_path, 'r', encoding='utf-8') as handle:
            body = render_markdown(handle.read(), doc_dir=os.path.dirname(relative))
        return render_template(
            'knowledge_view.html',
            title=os.path.basename(full_path),
            body=body,
            relative=relative,
            simulated=True,
        )


def register_error_handlers(app: Flask) -> None:
    """Register custom error page handlers."""

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return render_template('error.html', error_code=404, error_message='Page not found'), 404

    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors."""
        logging.exception('Internal server error')
        return render_template(
            'error.html',
            error_code=500,
            error_message='An internal server error occurred',
        ), 500

    @app.errorhandler(413)
    def too_large(error):
        """Handle file too large errors."""
        flash('File exceeds the maximum size of 16MB.', 'error')
        return redirect(url_for('upload'))


def _format_file_size(size_bytes: int) -> str:
    """Format byte size for human-readable display."""
    if size_bytes < 1024:
        return f'{size_bytes} B'
    if size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    return f'{size_bytes / (1024 * 1024):.1f} MB'


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
