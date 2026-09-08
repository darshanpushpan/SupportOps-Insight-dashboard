"""Parse simulated authentication and application logs for dashboard cards."""

import os
import re
from collections import Counter
from typing import Any, Dict, List

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AUTH_LOG = os.path.join(BASE_DIR, 'logs', 'authentication.log')
APP_LOG = os.path.join(BASE_DIR, 'logs', 'application.log')

LINE_RE = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
    r'(?P<level>\S+)\s+\[(?P<service>[^\]]+)\]\s+\[(?P<host>[^\]]+)\]\s+(?P<message>.+)$'
)
KV_RE = re.compile(r'(\w+)=([^\s]+)')


def _read_parsed(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if not os.path.exists(path):
        return rows
    with open(path, 'r', encoding='utf-8', errors='replace') as handle:
        for raw in handle:
            match = LINE_RE.match(raw.strip())
            if not match:
                continue
            row = match.groupdict()
            row.update(dict(KV_RE.findall(row['message'])))
            rows.append(row)
    return rows


def auth_signals(threshold: int = 3) -> Dict[str, Any]:
    """Summarize authentication.log for the operations dashboard."""
    rows = _read_parsed(AUTH_LOG)
    events = Counter(row.get('event', 'unknown') for row in rows)
    failed_by_user = Counter(
        row.get('user', 'unknown') for row in rows if row.get('event') == 'failed_login'
    )
    locked = sorted({row.get('user', 'unknown') for row in rows if row.get('event') == 'account_lockout'})
    mfa_users = sorted({
        row.get('user', 'unknown')
        for row in rows
        if row.get('event') in {'mfa_failure', 'mfa_enrollment_mismatch'}
    })
    over = [(user, count) for user, count in failed_by_user.most_common() if count >= threshold]
    return {
        'available': bool(rows),
        'total_events': len(rows),
        'failed_logins': events.get('failed_login', 0),
        'lockouts': events.get('account_lockout', 0),
        'mfa_errors': events.get('mfa_failure', 0) + events.get('mfa_enrollment_mismatch', 0),
        'successful_logins': events.get('login_success', 0),
        'locked_accounts': locked,
        'mfa_users': mfa_users,
        'over_threshold': over,
        'threshold': threshold,
        'source': 'logs/authentication.log (simulated)',
    }


def app_signals() -> Dict[str, Any]:
    """Summarize application.log health for the operations dashboard."""
    rows = _read_parsed(APP_LOG)
    health = [row for row in rows if row.get('event') == 'health_check']
    apis = [row for row in rows if row.get('event') == 'api_response']
    jobs = [row for row in rows if row.get('event') == 'background_job']

    health_ok = sum(1 for row in health if row.get('result') == 'ok' or row.get('status') == '200')
    api_times = []
    for row in apis:
        try:
            api_times.append(int(row.get('time_ms', '0')))
        except ValueError:
            continue
    avg_api = round(sum(api_times) / len(api_times), 1) if api_times else None
    health_rate = round(100 * health_ok / len(health), 1) if health else None
    jobs_ok = sum(1 for row in jobs if row.get('status') == 'success')

    status = 'Healthy (simulated)'
    if health and health_rate is not None and health_rate < 100:
        status = 'Degraded (simulated)'

    return {
        'available': bool(rows),
        'total_events': len(rows),
        'service_status': status,
        'health_checks': len(health),
        'health_success_rate': health_rate,
        'avg_api_ms': avg_api,
        'jobs_success': jobs_ok,
        'jobs_total': len(jobs),
        'source': 'logs/application.log (simulated)',
    }


def recommended_actions(auth: Dict[str, Any], app: Dict[str, Any]) -> List[str]:
    """Plain-language support insights from simulated signals."""
    actions = []
    if auth.get('lockouts'):
        actions.append(
            f"{auth['lockouts']} account lockout event(s) in the sample window. "
            'Triage as a possible multi-user access incident before treating each ticket in isolation.'
        )
    if auth.get('over_threshold'):
        names = ', '.join(user for user, _ in auth['over_threshold'])
        actions.append(
            f"Users at or above the failed-login threshold ({auth['threshold']}): {names}. "
            'Alerting at 3 failures in 15 minutes would have surfaced this cluster.'
        )
    if auth.get('mfa_errors'):
        actions.append(
            'MFA failures are present. Ask about device replacement and follow the MFA runbook; '
            'do not reset passwords for MFA-only failures.'
        )
    if app.get('service_status', '').startswith('Healthy'):
        actions.append(
            'OrderFlow health checks and jobs look normal in the sample. '
            'Communicate that this is an authentication/access issue, not an application outage.'
        )
    actions.append(
        'Follow identity-verification policy before unlocks or password resets. '
        'Link password-reset guidance in unlock tickets.'
    )
    return actions
