"""Load and filter simulated support tickets from JSON."""

import json
import os
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data')
TICKETS_PATH = os.path.join(DATA_DIR, 'tickets.json')


def load_tickets() -> List[Dict[str, Any]]:
    """Return all simulated tickets from data/tickets.json."""
    with open(TICKETS_PATH, 'r', encoding='utf-8') as handle:
        payload = json.load(handle)
    return payload.get('tickets', [])


def get_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Return a single ticket by ID, or None if not found."""
    for ticket in load_tickets():
        if ticket.get('ticket_id') == ticket_id:
            return ticket
    return None


def filter_tickets(
    tickets: List[Dict[str, Any]],
    status: str = '',
    priority: str = '',
    category: str = '',
    environment: str = '',
    assigned_group: str = '',
    sla_status: str = '',
    date_from: str = '',
    date_to: str = '',
) -> List[Dict[str, Any]]:
    """Filter tickets using dashboard query parameters."""
    filtered = tickets

    def _match(field: str, value: str) -> List[Dict[str, Any]]:
        if not value:
            return filtered
        return [t for t in filtered if str(t.get(field, '')) == value]

    filtered = _match('status', status)
    filtered = _match('priority', priority)
    filtered = _match('category', category)
    filtered = _match('environment', environment)
    filtered = _match('assigned_group', assigned_group)
    filtered = _match('sla_status', sla_status)

    if date_from:
        filtered = [
            t for t in filtered
            if str(t.get('created_at', ''))[:10] >= date_from
        ]
    if date_to:
        filtered = [
            t for t in filtered
            if str(t.get('created_at', ''))[:10] <= date_to
        ]

    filtered.sort(key=lambda t: str(t.get('created_at', '')), reverse=True)
    return filtered


def unique_values(tickets: List[Dict[str, Any]], field: str) -> List[str]:
    """Sorted unique values for a filter dropdown."""
    values = {str(t.get(field, '')) for t in tickets if t.get(field)}
    return sorted(values)


def _average(values: List[Optional[int]]) -> Optional[float]:
    numbers = [v for v in values if isinstance(v, (int, float))]
    if not numbers:
        return None
    return round(sum(numbers) / len(numbers), 1)


def compute_ticket_metrics(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build KPI and chart-ready summaries for simulated tickets."""
    total = len(tickets)
    by_status = Counter(t.get('status', 'Unknown') for t in tickets)
    by_priority = Counter(t.get('priority', 'Unknown') for t in tickets)
    by_category = Counter(t.get('category', 'Unknown') for t in tickets)
    by_group = Counter(t.get('assigned_group', 'Unknown') for t in tickets)
    by_sla = Counter(t.get('sla_status', 'Unknown') for t in tickets)

    open_like = by_status.get('Open', 0) + by_status.get('In Progress', 0) + by_status.get('Escalated', 0)
    resolved_like = by_status.get('Resolved', 0) + by_status.get('Closed', 0)

    first_response = _average([t.get('first_response_minutes') for t in tickets])
    resolution = _average([t.get('resolution_minutes') for t in tickets if t.get('resolution_minutes')])

    volume_by_day: Dict[str, int] = {}
    for ticket in tickets:
        day = str(ticket.get('created_at', ''))[:10]
        if day:
            volume_by_day[day] = volume_by_day.get(day, 0) + 1
    volume_series = [{'date': day, 'count': volume_by_day[day]} for day in sorted(volume_by_day)]

    recurring = [
        {'category': name, 'count': count}
        for name, count in by_category.most_common()
        if count >= 2
    ]

    priority_rank = {'P1': 0, 'P2': 1, 'P3': 2, 'P4': 3}
    high_priority = [
        t for t in tickets
        if t.get('priority') in {'P1', 'P2'}
        and t.get('status') in {'Open', 'In Progress', 'Escalated'}
    ]
    high_priority.sort(key=lambda t: (priority_rank.get(t.get('priority'), 9), t.get('created_at', '')))

    recent = sorted(tickets, key=lambda t: t.get('updated_at', ''), reverse=True)[:8]

    return {
        'total': total,
        'open': open_like,
        'resolved': resolved_like,
        'by_status': dict(by_status),
        'by_priority': dict(by_priority),
        'by_category': dict(by_category),
        'by_group': dict(by_group),
        'by_sla': dict(by_sla),
        'avg_first_response_minutes': first_response,
        'avg_resolution_minutes': resolution,
        'volume_series': volume_series,
        'recurring': recurring,
        'high_priority': high_priority,
        'recent': recent,
        'data_note': 'Simulated Support Data — Northstar Retail / OrderFlow (fictional).',
    }


def bar_rows(counts: Dict[str, int], preferred_order: Optional[List[str]] = None) -> List[Tuple[str, int, int]]:
    """Convert a count dict into rows with percentage of max for CSS bars."""
    if not counts:
        return []
    if preferred_order:
        items = [(key, counts.get(key, 0)) for key in preferred_order if key in counts]
        for key, value in counts.items():
            if key not in preferred_order:
                items.append((key, value))
    else:
        items = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    peak = max(value for _, value in items) or 1
    return [(name, value, int(round(100 * value / peak))) for name, value in items]
