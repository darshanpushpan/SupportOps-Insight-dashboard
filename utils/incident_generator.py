"""HTML incident report generation for SupportOps Insight."""

from datetime import datetime
from html import escape
from typing import Any, Dict, List, Optional

from utils.severity_classifier import SeverityClassifier


class IncidentGenerator:
    """Generate professional HTML incident reports from log data."""

    SEVERITY_COLORS = {
        'CRITICAL': '#dc3545',
        'HIGH': '#c9302c',
        'MEDIUM': '#f0ad4e',
        'LOW': '#5cb85c',
    }

    LEVEL_COLORS = {
        'DEBUG': '#6c757d',
        'INFO': '#28a745',
        'WARNING': '#ffc107',
        'ERROR': '#fd7e14',
        'CRITICAL': '#dc3545',
    }

    RECOMMENDED_ACTIONS = [
        'Review affected services and hosts',
        'Investigate top error messages for root cause',
        'Check service health and restart if necessary',
        'Monitor for recurrence over next 24 hours',
        'Document findings and update runbooks',
    ]

    def __init__(self, classifier: Optional[SeverityClassifier] = None):
        """
        Initialize the incident generator.

        Args:
            classifier: Optional SeverityClassifier instance.
        """
        self.classifier = classifier or SeverityClassifier()

    def generate_report(
        self,
        logs: List[Dict[str, Any]],
        source_filename: str = 'Unknown',
        notes: str = '',
        error_groups: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Generate a complete HTML incident report.

        Args:
            logs: Log entries included in the report.
            source_filename: Name of the source log file.
            notes: Optional user-provided notes.
            error_groups: Pre-computed error groups (optional).

        Returns:
            HTML string for the incident report.
        """
        report_id = f'INC-{datetime.now().strftime("%Y%m%d%H%M%S")}'
        generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        severity = self.classifier.get_overall_severity(logs)
        severity_color = self.SEVERITY_COLORS.get(severity, '#6c757d')

        if error_groups is None:
            error_groups = self.classifier.group_errors(logs)

        services = sorted({log.get('service', 'Unknown') for log in logs})
        hosts = sorted({log.get('host', 'Unknown') for log in logs})
        error_count = sum(1 for log in logs if log.get('level', '').upper() in {'ERROR', 'CRITICAL'})
        critical_count = sum(1 for log in logs if log.get('level', '').upper() == 'CRITICAL')
        time_range = self._get_time_range(logs)
        top_errors = error_groups[:10]
        display_logs = logs[:100]

        return self._render_html(
            report_id=report_id,
            generated_at=generated_at,
            severity=severity,
            severity_color=severity_color,
            logs=logs,
            display_logs=display_logs,
            source_filename=source_filename,
            notes=notes,
            services=services,
            hosts=hosts,
            error_count=error_count,
            critical_count=critical_count,
            time_range=time_range,
            top_errors=top_errors,
        )

    def save_report(
        self,
        logs: List[Dict[str, Any]],
        output_path: str,
        source_filename: str = 'Unknown',
        notes: str = '',
        error_groups: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Generate and save an HTML incident report to disk.

        Args:
            logs: Log entries for the report.
            output_path: Destination file path.
            source_filename: Source log filename.
            notes: Optional user notes.
            error_groups: Pre-computed error groups.

        Returns:
            Report ID string.
        """
        html = self.generate_report(logs, source_filename, notes, error_groups)
        report_id = f'INC-{datetime.now().strftime("%Y%m%d%H%M%S")}'

        with open(output_path, 'w', encoding='utf-8') as handle:
            handle.write(html)

        return report_id

    def _get_time_range(self, logs: List[Dict[str, Any]]) -> str:
        """Compute the time range covered by log entries."""
        timestamps = []
        for log in logs:
            ts = log.get('parsed_timestamp') or log.get('timestamp')
            if ts:
                timestamps.append(str(ts))

        if not timestamps:
            return 'Unknown'

        timestamps.sort()
        if len(timestamps) == 1:
            return timestamps[0]
        return f'{timestamps[0]} to {timestamps[-1]}'

    def _render_html(
        self,
        report_id: str,
        generated_at: str,
        severity: str,
        severity_color: str,
        logs: List[Dict[str, Any]],
        display_logs: List[Dict[str, Any]],
        source_filename: str,
        notes: str,
        services: List[str],
        hosts: List[str],
        error_count: int,
        critical_count: int,
        time_range: str,
        top_errors: List[Dict[str, Any]],
    ) -> str:
        """Render the full HTML report document."""
        service_tags = ''.join(
            f'<span class="tag">{escape(service)}</span>' for service in services
        )
        host_tags = ''.join(
            f'<span class="tag">{escape(host)}</span>' for host in hosts
        )

        error_boxes = ''
        for group in top_errors:
            error_boxes += f'''
            <div class="error-box">
                <div class="error-count">{group["count"]} occurrences</div>
                <pre>{escape(group["sample_message"])}</pre>
            </div>
            '''

        log_rows = ''
        for log in display_logs:
            level = str(log.get('level', 'INFO')).upper()
            level_color = self.LEVEL_COLORS.get(level, '#6c757d')
            timestamp = escape(str(log.get('parsed_timestamp') or log.get('timestamp') or 'N/A'))
            log_rows += f'''
            <tr>
                <td>{timestamp}</td>
                <td><span class="badge" style="background-color:{level_color}">{level}</span></td>
                <td>{escape(str(log.get("service", "Unknown")))}</td>
                <td>{escape(str(log.get("host", "Unknown")))}</td>
                <td class="message-cell">{escape(str(log.get("message", "")))}</td>
            </tr>
            '''

        action_items = ''.join(
            f'<li>{escape(action)}</li>' for action in self.RECOMMENDED_ACTIONS
        )

        notes_section = ''
        if notes.strip():
            notes_section = f'''
            <div class="card">
                <h2>Additional Notes</h2>
                <p>{escape(notes)}</p>
            </div>
            '''

        truncated_note = ''
        if len(logs) > 100:
            truncated_note = f'<p class="note">Showing first 100 of {len(logs)} log entries.</p>'

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Incident Report - {escape(report_id)}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
        }}
        .report-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        .report-header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        .report-meta {{ opacity: 0.9; font-size: 0.95rem; }}
        .severity-badge {{
            display: inline-block;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 1rem;
            color: white;
            background-color: {severity_color};
        }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }}
        .card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .card h2 {{
            color: #667eea;
            margin-bottom: 1rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.5rem;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }}
        .stat-box {{
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 6px;
            text-align: center;
        }}
        .stat-value {{ font-size: 1.8rem; font-weight: bold; color: #667eea; }}
        .stat-label {{ font-size: 0.85rem; color: #666; }}
        .tags {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .tag {{
            background: #667eea;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.85rem;
        }}
        .error-box {{
            background: #fff5f5;
            border-left: 4px solid #dc3545;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 4px;
        }}
        .error-count {{ font-weight: bold; color: #dc3545; margin-bottom: 0.5rem; }}
        .error-box pre {{
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            word-break: break-word;
            font-size: 0.9rem;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #667eea; color: white; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            color: white;
            font-size: 0.75rem;
            font-weight: bold;
        }}
        .message-cell {{ max-width: 400px; word-break: break-word; }}
        .actions ul {{ padding-left: 1.5rem; }}
        .actions li {{ margin-bottom: 0.5rem; }}
        .report-footer {{
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid #dee2e6;
            margin-top: 2rem;
        }}
        .print-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            margin-bottom: 1rem;
        }}
        .print-btn:hover {{ background: #5a6fd6; }}
        .note {{ color: #666; font-style: italic; margin-top: 0.5rem; }}
        @media print {{
            .print-btn {{ display: none; }}
            body {{ background: white; }}
            .card {{ box-shadow: none; border: 1px solid #dee2e6; }}
        }}
        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: 1fr 1fr; }}
            table {{ font-size: 0.8rem; }}
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <h1>🚨 Incident Report</h1>
        <div class="report-meta">Generated: {escape(generated_at)}</div>
        <div class="severity-badge">Severity: {escape(severity)}</div>
    </div>

    <div class="container">
        <div class="card">
            <h2>Incident Summary</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">{len(logs)}</div>
                    <div class="stat-label">Total Log Entries</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{error_count}</div>
                    <div class="stat-label">Error Count</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{critical_count}</div>
                    <div class="stat-label">Critical Errors</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{len(services)}</div>
                    <div class="stat-label">Services Affected</div>
                </div>
            </div>
            <p style="margin-top:1rem;"><strong>Time Range:</strong> {escape(time_range)}</p>
            <p><strong>Source File:</strong> {escape(source_filename)}</p>
        </div>

        {notes_section}

        <div class="card">
            <h2>Affected Components</h2>
            <h3>Services</h3>
            <div class="tags">{service_tags or '<span class="tag">None</span>'}</div>
            <h3 style="margin-top:1rem;">Hosts</h3>
            <div class="tags">{host_tags or '<span class="tag">None</span>'}</div>
        </div>

        <div class="card">
            <h2>Top Error Messages</h2>
            {error_boxes or '<p>No grouped errors found.</p>'}
        </div>

        <div class="card">
            <h2>Detailed Log Entries</h2>
            {truncated_note}
            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Level</th>
                            <th>Service</th>
                            <th>Host</th>
                            <th>Message</th>
                        </tr>
                    </thead>
                    <tbody>
                        {log_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card actions">
            <h2>Recommended Actions</h2>
            <ul>{action_items}</ul>
        </div>
    </div>

    <div class="report-footer">
        <button class="print-btn" onclick="window.print()">Print Report</button>
        <p>Report ID: {escape(report_id)}</p>
        <p>SupportOps Insight - Production Support Dashboard</p>
    </div>
</body>
</html>'''
