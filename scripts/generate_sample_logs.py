"""Generate deterministic fictional authentication and application logs.

All usernames, hosts, and IPs are simulated for the Northstar Retail /
OrderFlow portfolio scenario. No real credentials are written.
"""

import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOG_DIR = os.path.join(BASE, 'logs')

HOST = 'app-server-01'
AUTH_SVC = 'AuthService'
APP_SVC = 'OrderFlow'


def line(ts, level, service, host, message):
    """Standard SupportOps Insight log line."""
    return f'{ts} {level} [{service}] [{host}] {message}'


def auth_events():
    """Build 100+ fictional auth events for 17 Aug 2026 morning."""
    events = []

    # Overnight / early successful traffic
    for hour, minute, user, ip in [
        (6, 5, 'support.agent01', '10.10.10.20'),
        (6, 18, 'support.agent02', '10.10.10.21'),
        (6, 42, 'ops.supervisor01', '10.10.30.11'),
        (7, 2, 'merch.planner01', '10.10.40.15'),
        (7, 15, 'store.associate01', '10.10.50.8'),
        (7, 28, 'finance.coordinator02', '10.10.21.40'),
        (7, 40, 'ops.coordinator04', '10.10.30.18'),
        (7, 48, 'support.agent01', '10.10.10.20'),
    ]:
        events.append((
            f'2026-08-17 {hour:02d}:{minute:02d}:00',
            'INFO',
            f'event=login_success user={user} src_ip={ip} host=northstar.example.com note=simulated',
        ))
        events.append((
            f'2026-08-17 {hour:02d}:{minute:02d}:08',
            'INFO',
            f'event=session_refresh user={user} src_ip={ip} note=simulated',
        ))

    # Password resets that start the incident chain
    events.append((
        '2026-08-17 07:51:12',
        'INFO',
        'event=password_reset user=finance.analyst01 src_ip=10.10.21.14 note=simulated',
    ))
    events.append((
        '2026-08-17 07:54:03',
        'INFO',
        'event=password_reset user=finance.analyst02 src_ip=10.10.21.15 note=simulated',
    ))
    events.append((
        '2026-08-17 08:04:22',
        'INFO',
        'event=password_reset user=finance.coordinator01 src_ip=10.10.21.16 note=simulated',
    ))
    events.append((
        '2026-08-17 08:07:40',
        'INFO',
        'event=password_reset user=ops.coordinator01 src_ip=10.10.30.12 note=simulated',
    ))

    # finance.analyst01 — failed logins then lockout then unlock
    for sec, reason in [
        (8, 'invalid_credentials'),
        (32, 'invalid_credentials'),
        (51, 'invalid_credentials'),
    ]:
        events.append((
            f'2026-08-17 08:08:{sec:02d}',
            'ERROR',
            f'event=failed_login user=finance.analyst01 src_ip=10.10.21.14 reason={reason} note=simulated',
        ))
    events.append((
        '2026-08-17 08:10:04',
        'WARNING',
        'event=account_lockout user=finance.analyst01 src_ip=10.10.21.14 reason=threshold_exceeded note=simulated',
    ))
    events.append((
        '2026-08-17 08:10:20',
        'ERROR',
        'event=failed_login user=finance.analyst01 src_ip=10.10.21.14 reason=account_locked note=simulated',
    ))
    events.append((
        '2026-08-17 10:18:00',
        'INFO',
        'event=account_unlock user=finance.analyst01 actor=support.agent01 note=simulated',
    ))
    events.append((
        '2026-08-17 10:19:12',
        'INFO',
        'event=login_success user=finance.analyst01 src_ip=10.10.21.14 note=simulated',
    ))

    # finance.analyst02
    for sec in (10, 28, 44):
        events.append((
            f'2026-08-17 08:12:{sec:02d}',
            'ERROR',
            'event=failed_login user=finance.analyst02 src_ip=10.10.21.15 reason=invalid_credentials note=simulated',
        ))
    events.append((
        '2026-08-17 08:13:02',
        'WARNING',
        'event=account_lockout user=finance.analyst02 src_ip=10.10.21.15 reason=threshold_exceeded note=simulated',
    ))
    events.append((
        '2026-08-17 10:22:00',
        'INFO',
        'event=account_unlock user=finance.analyst02 actor=support.agent01 note=simulated',
    ))
    events.append((
        '2026-08-17 10:23:40',
        'INFO',
        'event=login_success user=finance.analyst02 src_ip=10.10.21.15 note=simulated',
    ))

    # ops.coordinator01
    for sec in (5, 18, 33, 47):
        events.append((
            f'2026-08-17 08:19:{sec:02d}',
            'ERROR',
            'event=failed_login user=ops.coordinator01 src_ip=10.10.30.12 reason=invalid_credentials note=simulated',
        ))
    events.append((
        '2026-08-17 08:21:10',
        'WARNING',
        'event=account_lockout user=ops.coordinator01 src_ip=10.10.30.12 reason=threshold_exceeded note=simulated',
    ))
    events.append((
        '2026-08-17 11:00:00',
        'INFO',
        'event=account_unlock user=ops.coordinator01 actor=support.agent02 note=simulated',
    ))
    events.append((
        '2026-08-17 11:02:15',
        'INFO',
        'event=login_success user=ops.coordinator01 src_ip=10.10.30.12 note=simulated',
    ))

    # finance.coordinator01 — failed old password, no lockout
    events.append((
        '2026-08-17 08:10:40',
        'ERROR',
        'event=failed_login user=finance.coordinator01 src_ip=10.10.21.16 reason=invalid_credentials note=simulated',
    ))
    events.append((
        '2026-08-17 08:11:05',
        'ERROR',
        'event=failed_login user=finance.coordinator01 src_ip=10.10.21.16 reason=invalid_credentials note=simulated',
    ))
    events.append((
        '2026-08-17 09:12:00',
        'INFO',
        'event=login_success user=finance.coordinator01 src_ip=10.10.21.16 note=simulated',
    ))

    # MFA failures / enrollment mismatch
    events.append((
        '2026-08-17 08:25:10',
        'ERROR',
        'event=mfa_failure user=ops.coordinator02 src_ip=10.10.30.13 reason=enrollment_mismatch note=simulated',
    ))
    events.append((
        '2026-08-17 08:25:40',
        'ERROR',
        'event=mfa_failure user=ops.coordinator02 src_ip=10.10.30.13 reason=enrollment_mismatch note=simulated',
    ))
    events.append((
        '2026-08-17 08:26:05',
        'WARNING',
        'event=mfa_enrollment_mismatch user=ops.coordinator02 src_ip=10.10.30.13 reason=stale_device note=simulated',
    ))
    events.append((
        '2026-08-17 11:38:00',
        'INFO',
        'event=mfa_reenroll user=ops.coordinator02 actor=support.agent02 note=simulated',
    ))
    events.append((
        '2026-08-17 11:39:20',
        'INFO',
        'event=login_success user=ops.coordinator02 src_ip=10.10.30.13 note=simulated',
    ))

    events.append((
        '2026-08-17 08:34:12',
        'ERROR',
        'event=mfa_failure user=finance.analyst03 src_ip=10.10.21.17 reason=invalid_code note=simulated',
    ))
    events.append((
        '2026-08-17 08:34:48',
        'ERROR',
        'event=mfa_failure user=finance.analyst03 src_ip=10.10.21.17 reason=invalid_code note=simulated',
    ))
    events.append((
        '2026-08-17 08:35:10',
        'WARNING',
        'event=mfa_enrollment_mismatch user=finance.analyst03 src_ip=10.10.21.17 reason=stale_factor note=simulated',
    ))
    events.append((
        '2026-08-17 11:55:00',
        'INFO',
        'event=mfa_reenroll user=finance.analyst03 actor=support.agent01 note=simulated',
    ))
    events.append((
        '2026-08-17 11:56:30',
        'INFO',
        'event=login_success user=finance.analyst03 src_ip=10.10.21.17 note=simulated',
    ))

    # Benign successful logins throughout the morning
    benign_users = [
        ('08:02:00', 'ops.supervisor01', '10.10.30.11'),
        ('08:05:00', 'merch.planner02', '10.10.40.16'),
        ('08:16:00', 'store.associate02', '10.10.50.9'),
        ('08:22:00', 'support.agent02', '10.10.10.21'),
        ('08:28:00', 'finance.analyst04', '10.10.21.18'),
        ('08:31:00', 'ops.coordinator04', '10.10.30.18'),
        ('08:38:00', 'merch.planner01', '10.10.40.15'),
        ('08:44:00', 'store.associate03', '10.10.50.10'),
        ('08:50:00', 'support.agent01', '10.10.10.20'),
        ('08:58:00', 'ops.supervisor01', '10.10.30.11'),
        ('09:06:00', 'ops.supervisor01', '10.10.30.11'),
        ('09:12:00', 'merch.planner03', '10.10.40.19'),
        ('09:20:00', 'finance.analyst05', '10.10.21.19'),
        ('09:33:00', 'store.associate01', '10.10.50.8'),
        ('09:47:00', 'ops.coordinator05', '10.10.30.22'),
        ('10:02:00', 'support.agent02', '10.10.10.21'),
        ('10:30:00', 'merch.planner02', '10.10.40.16'),
        ('10:45:00', 'finance.coordinator02', '10.10.21.40'),
        ('11:10:00', 'store.associate04', '10.10.50.11'),
        ('11:25:00', 'ops.coordinator04', '10.10.30.18'),
        ('12:00:00', 'support.agent01', '10.10.10.20'),
        ('12:15:00', 'merch.planner01', '10.10.40.15'),
    ]
    for ts, user, ip in benign_users:
        events.append((
            f'2026-08-17 {ts}',
            'INFO',
            f'event=login_success user={user} src_ip={ip} host=northstar.example.com note=simulated',
        ))

    # Password policy / other benign
    for ts, user in [
        ('07:10:00', 'support.agent01'),
        ('09:01:00', 'ops.supervisor01'),
        ('10:05:00', 'finance.analyst04'),
        ('11:12:00', 'merch.planner01'),
    ]:
        events.append((
            f'2026-08-17 {ts}',
            'INFO',
            f'event=password_policy_ok user={user} note=simulated',
        ))

    # Two extra failed logins below threshold
    events.append((
        '2026-08-17 09:40:00',
        'ERROR',
        'event=failed_login user=store.associate06 src_ip=10.10.50.20 reason=invalid_credentials note=simulated',
    ))
    events.append((
        '2026-08-17 09:41:00',
        'ERROR',
        'event=failed_login user=store.associate06 src_ip=10.10.50.20 reason=invalid_credentials note=simulated',
    ))
    events.append((
        '2026-08-17 09:42:10',
        'INFO',
        'event=login_success user=store.associate06 src_ip=10.10.50.20 note=simulated',
    ))

    # Intentional malformed lines for the analyzer to skip
    # (written separately)

    return events


def app_events():
    """Build 25+ fictional OrderFlow application events showing a healthy app."""
    events = []
    checks = [
        ('07:00:00', 22),
        ('07:15:00', 24),
        ('07:30:00', 21),
        ('07:45:00', 25),
        ('08:00:00', 28),
        ('08:15:00', 30),
        ('08:30:00', 27),
        ('08:45:00', 26),
        ('09:00:00', 29),
        ('09:15:00', 31),
        ('09:30:00', 28),
        ('10:00:00', 27),
        ('10:30:00', 25),
        ('11:00:00', 24),
        ('12:00:00', 23),
    ]
    for ts, ms in checks:
        events.append((
            f'2026-08-17 {ts}',
            'INFO',
            f'event=health_check path=/health status=200 time_ms={ms} result=ok note=simulated',
        ))

    apis = [
        ('08:05:00', '/orders', 95),
        ('08:20:00', '/inventory', 110),
        ('08:40:00', '/waves', 140),
        ('09:10:00', '/reports', 180),
        ('09:50:00', '/orders', 88),
        ('10:20:00', '/checkout', 102),
        ('11:05:00', '/orders', 91),
        ('12:10:00', '/inventory', 99),
    ]
    for ts, path, ms in apis:
        events.append((
            f'2026-08-17 {ts}',
            'INFO',
            f'event=api_response path={path} status=200 time_ms={ms} note=simulated',
        ))

    jobs = [
        ('07:15:00', 'settlement_export'),
        ('08:00:00', 'inventory_sync'),
        ('09:00:00', 'pick_wave_build'),
        ('10:00:00', 'cache_warmup'),
        ('11:00:00', 'inventory_sync'),
        ('12:00:00', 'order_aging'),
    ]
    for ts, job in jobs:
        events.append((
            f'2026-08-17 {ts}',
            'INFO',
            f'event=background_job job={job} status=success env=production note=simulated',
        ))

    events.append((
        '2026-08-17 08:12:00',
        'INFO',
        'event=db_status result=ok pool=healthy note=simulated',
    ))
    events.append((
        '2026-08-17 10:16:00',
        'WARNING',
        'event=validation_error sku=GC-SIM-100 path=/orders result=rejected note=simulated isolated_sku',
    ))
    events.append((
        '2026-08-17 12:31:00',
        'INFO',
        'event=cache_status status=refresh_ok note=simulated',
    ))
    events.append((
        '2026-08-17 08:35:00',
        'INFO',
        'event=scheduler status=running next=inventory_sync note=simulated',
    ))
    return events


def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    auth_path = os.path.join(LOG_DIR, 'authentication.log')
    app_path = os.path.join(LOG_DIR, 'application.log')

    auth_lines = [line(ts, lvl, AUTH_SVC, HOST, msg) for ts, lvl, msg in auth_events()]
    auth_lines.append('THIS LINE IS MALFORMED AND SHOULD BE SKIPPED')
    auth_lines.append('??? not-a-log-line')
    auth_lines.append('')

    app_lines = [line(ts, lvl, APP_SVC, HOST, msg) for ts, lvl, msg in app_events()]

    with open(auth_path, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(auth_lines).strip() + '\n')
    with open(app_path, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(app_lines).strip() + '\n')

    print(f'Wrote {len([x for x in auth_lines if x])} auth lines (including 2 malformed) to {auth_path}')
    print(f'Wrote {len(app_lines)} application lines to {app_path}')


if __name__ == '__main__':
    main()
