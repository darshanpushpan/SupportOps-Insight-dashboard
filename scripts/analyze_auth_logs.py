"""Analyze fictional authentication.log and write a Markdown summary.

Uses the Python standard library only.
"""

import argparse
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_LOG = os.path.join(BASE, 'logs', 'authentication.log')
DEFAULT_OUT = os.path.join(BASE, 'reports', 'log-analysis-summary.md')

LINE_RE = re.compile(
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
    r'(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+'
    r'\[(?P<service>[^\]]+)\]\s+'
    r'\[(?P<host>[^\]]+)\]\s+'
    r'(?P<message>.+)$',
    re.IGNORECASE,
)

KV_RE = re.compile(r'(\w+)=([^\s]+)')


def parse_message(message):
    """Pull key=value pairs from a log message."""
    data = dict(KV_RE.findall(message))
    data['raw'] = message
    return data


def analyze(path, threshold):
    """Parse auth log and return summary statistics."""
    parsed = []
    skipped = 0

    with open(path, 'r', encoding='utf-8', errors='replace') as handle:
        for line_number, raw in enumerate(handle, start=1):
            stripped = raw.strip()
            if not stripped:
                continue
            match = LINE_RE.match(stripped)
            if not match:
                skipped += 1
                continue
            row = match.groupdict()
            row.update(parse_message(row['message']))
            row['line_number'] = line_number
            parsed.append(row)

    events = Counter(row.get('event', 'unknown') for row in parsed)
    failed_by_user = Counter(
        row.get('user', 'unknown')
        for row in parsed
        if row.get('event') == 'failed_login'
    )
    locked = sorted({
        row.get('user', 'unknown')
        for row in parsed
        if row.get('event') == 'account_lockout'
    })
    unlocked = sorted({
        row.get('user', 'unknown')
        for row in parsed
        if row.get('event') == 'account_unlock'
    })
    mfa_failures = [
        row for row in parsed
        if row.get('event') in {'mfa_failure', 'mfa_enrollment_mismatch'}
    ]
    over_threshold = [
        (user, count) for user, count in failed_by_user.most_common()
        if count >= threshold
    ]

    timestamps = [row['timestamp'] for row in parsed]
    window = f'{min(timestamps)} to {max(timestamps)}' if timestamps else 'n/a'

    recommendations = []
    if over_threshold:
        recommendations.append(
            f'Alert after {threshold} failed logins (observed users: '
            + ', '.join(user for user, _ in over_threshold)
            + ').'
        )
    if locked:
        recommendations.append(
            'Treat clustered lockouts as a multi-user access incident, not isolated password mistakes.'
        )
        recommendations.append(
            'Link password-reset guidance before unlock workflows so users do not retry the old password.'
        )
    if mfa_failures:
        recommendations.append(
            'Review MFA enrollment after device replacement or authenticator reset.'
        )
    recommendations.append(
        'Keep application health checks in view so access issues are not declared as OrderFlow outages.'
    )
    recommendations.append(
        'Follow company access-control and identity-verification policy before unlocking accounts or resetting passwords.'
    )

    return {
        'path': path,
        'parsed': len(parsed),
        'skipped': skipped,
        'events': events,
        'failed_by_user': failed_by_user,
        'locked': locked,
        'unlocked': unlocked,
        'mfa_failures': mfa_failures,
        'over_threshold': over_threshold,
        'threshold': threshold,
        'window': window,
        'recommendations': recommendations,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def render_markdown(summary):
    """Build the Markdown report body."""
    lines = [
        '# Authentication Log Analysis Summary',
        '',
        '**Simulated Support Data.** Northstar Retail / OrderFlow is fictional. '
        'This report is generated from `logs/authentication.log` for portfolio demonstration only.',
        '',
        f'- Generated at: {summary["generated_at"]}',
        f'- Source: `{os.path.basename(summary["path"])}`',
        f'- Parsed events: {summary["parsed"]}',
        f'- Malformed lines skipped: {summary["skipped"]}',
        f'- Time window: {summary["window"]}',
        f'- Failed-login threshold: {summary["threshold"]}',
        '',
        '## Event counts',
        '',
        '| Event | Count |',
        '| --- | ---: |',
    ]
    for event, count in summary['events'].most_common():
        lines.append(f'| {event} | {count} |')

    lines.extend(['', '## Failed logins by user', '', '| User | Failed logins | Over threshold |', '| --- | ---: | --- |'])
    for user, count in summary['failed_by_user'].most_common():
        flag = 'Yes' if count >= summary['threshold'] else 'No'
        lines.append(f'| {user} | {count} | {flag} |')
    if not summary['failed_by_user']:
        lines.append('| (none) | 0 | No |')

    lines.extend(['', '## Locked accounts', ''])
    if summary['locked']:
        for user in summary['locked']:
            lines.append(f'- {user}')
    else:
        lines.append('- None')

    lines.extend(['', '## Unlocked accounts', ''])
    if summary['unlocked']:
        for user in summary['unlocked']:
            lines.append(f'- {user}')
    else:
        lines.append('- None')

    lines.extend(['', '## MFA failures and enrollment mismatch', ''])
    if summary['mfa_failures']:
        by_user = defaultdict(list)
        for row in summary['mfa_failures']:
            by_user[row.get('user', 'unknown')].append(row.get('event'))
        for user, kinds in sorted(by_user.items()):
            lines.append(f'- {user}: {", ".join(kinds)}')
    else:
        lines.append('- None')

    lines.extend(['', '## Recommended support actions', ''])
    for item in summary['recommendations']:
        lines.append(f'- {item}')

    lines.extend([
        '',
        '## Interpretation',
        '',
        'Repeated failed logins after password resets created account lockouts. '
        'A smaller set of stale MFA enrollments caused verification failures. '
        'Successful logins continued for other users throughout the window, '
        'which supports treating this as an authentication/access incident rather than an OrderFlow outage.',
        '',
    ])
    return '\n'.join(lines)


def print_terminal(summary):
    """Print a readable terminal summary."""
    print('=== Auth log analysis (simulated) ===')
    print(f'Source: {summary["path"]}')
    print(f'Parsed: {summary["parsed"]}  Skipped: {summary["skipped"]}  Threshold: {summary["threshold"]}')
    print(f'Window: {summary["window"]}')
    print('Events:', dict(summary['events']))
    print('Failed logins by user:', dict(summary['failed_by_user']))
    print('Locked accounts:', ', '.join(summary['locked']) or 'none')
    print('MFA-related events:', len(summary['mfa_failures']))
    print('Users over threshold:', summary['over_threshold'])
    print('Recommendations:')
    for item in summary['recommendations']:
        print(f'  - {item}')


def main():
    parser = argparse.ArgumentParser(description='Analyze simulated authentication logs.')
    parser.add_argument('--log', default=DEFAULT_LOG, help='Path to authentication.log')
    parser.add_argument('--threshold', type=int, default=3, help='Failed-login threshold (default 3)')
    parser.add_argument('--out', default=DEFAULT_OUT, help='Markdown report output path')
    args = parser.parse_args()

    if not os.path.exists(args.log):
        raise SystemExit(f'Log file not found: {args.log}')

    summary = analyze(args.log, args.threshold)
    print_terminal(summary)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as handle:
        handle.write(render_markdown(summary))
    print(f'Wrote Markdown report: {args.out}')


if __name__ == '__main__':
    main()
