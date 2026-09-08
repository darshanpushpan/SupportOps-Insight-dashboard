"""Error grouping and severity scoring for SupportOps Insight."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil import parser as date_parser


class SeverityClassifier:
    """Classify log severity and group similar errors."""

    def __init__(
        self,
        severity_weights: Optional[Dict[str, int]] = None,
        critical_keywords: Optional[List[str]] = None,
        critical_services: Optional[List[str]] = None,
    ):
        """
        Initialize the severity classifier.

        Args:
            severity_weights: Mapping of log levels to numeric weights.
            critical_keywords: Keywords that increase severity score.
            critical_services: Service name keywords considered critical.
        """
        self.severity_weights = severity_weights or {
            'DEBUG': 1,
            'INFO': 2,
            'WARNING': 3,
            'ERROR': 4,
            'CRITICAL': 5,
        }
        self.critical_keywords = critical_keywords or []
        self.critical_services = critical_services or []

    def classify_log(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single log entry and compute a suggested severity score.

        Args:
            log_entry: Parsed log entry dictionary.

        Returns:
            Dictionary with base severity, score, and suggested level.
        """
        level = str(log_entry.get('level', 'INFO')).upper()
        base_severity = self.severity_weights.get(level, 2)
        score = base_severity

        message = str(log_entry.get('message', '')).lower()
        service = str(log_entry.get('service', '')).lower()

        for keyword in self.critical_keywords:
            if keyword.lower() in message:
                score += 1

        for keyword in self.critical_services:
            if keyword.lower() in service:
                score += 1

        score = min(score, 5)
        suggested_level = self._score_to_level(score)

        return {
            'base_severity': base_severity,
            'score': score,
            'suggested_level': suggested_level,
        }

    def group_errors(
        self,
        logs: List[Dict[str, Any]],
        pattern_length: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Group similar error messages and compute aggregate statistics.

        Args:
            logs: List of parsed log entries.
            pattern_length: Number of message characters used for grouping.

        Returns:
            Sorted list of error group dictionaries (most frequent first).
        """
        groups: Dict[str, Dict[str, Any]] = {}

        for log in logs:
            level = str(log.get('level', '')).upper()
            if level not in {'ERROR', 'CRITICAL', 'WARNING'}:
                continue

            message = str(log.get('message', ''))
            pattern = message[:pattern_length].strip()
            if not pattern:
                continue

            if pattern not in groups:
                groups[pattern] = {
                    'pattern': pattern,
                    'count': 0,
                    'services': set(),
                    'hosts': set(),
                    'levels': set(),
                    'messages': [],
                    'timestamps': [],
                    'sample_message': message,
                    'log_ids': [],
                }

            group = groups[pattern]
            group['count'] += 1
            group['services'].add(log.get('service', 'Unknown'))
            group['hosts'].add(log.get('host', 'Unknown'))
            group['levels'].add(level)
            group['messages'].append(message)
            group['log_ids'].append(log.get('id'))

            parsed_ts = log.get('parsed_timestamp') or log.get('timestamp')
            if parsed_ts:
                group['timestamps'].append(parsed_ts)

        result = []
        for pattern, group in groups.items():
            timestamps = self._sort_timestamps(group['timestamps'])
            result.append({
                'pattern': pattern,
                'count': group['count'],
                'services': sorted(group['services']),
                'hosts': sorted(group['hosts']),
                'levels': sorted(group['levels']),
                'time_range': self._format_time_range(timestamps),
                'sample_message': group['sample_message'],
                'log_ids': group['log_ids'],
            })

        result.sort(key=lambda item: item['count'], reverse=True)
        return result

    def get_overall_severity(self, logs: List[Dict[str, Any]]) -> str:
        """
        Determine overall incident severity from a list of logs.

        Args:
            logs: List of parsed log entries.

        Returns:
            Severity label: CRITICAL, HIGH, MEDIUM, or LOW.
        """
        if not logs:
            return 'LOW'

        max_score = 1
        for log in logs:
            classification = self.classify_log(log)
            max_score = max(max_score, classification['score'])

        if max_score >= 5:
            return 'CRITICAL'
        if max_score >= 4:
            return 'HIGH'
        if max_score >= 3:
            return 'MEDIUM'
        return 'LOW'

    def _score_to_level(self, score: int) -> str:
        """Convert numeric score to severity level label."""
        mapping = {
            1: 'DEBUG',
            2: 'INFO',
            3: 'WARNING',
            4: 'ERROR',
            5: 'CRITICAL',
        }
        return mapping.get(score, 'INFO')

    def _sort_timestamps(self, timestamps: List[str]) -> List[str]:
        """Sort timestamp strings chronologically."""
        parsed = []
        for ts in timestamps:
            try:
                parsed.append((date_parser.parse(str(ts)), str(ts)))
            except (ValueError, OverflowError, TypeError):
                parsed.append((datetime.min, str(ts)))

        parsed.sort(key=lambda item: item[0])
        return [item[1] for item in parsed]

    def _format_time_range(self, timestamps: List[str]) -> str:
        """Format a human-readable time range from timestamps."""
        if not timestamps:
            return 'Unknown'

        if len(timestamps) == 1:
            return timestamps[0]

        return f'{timestamps[0]} to {timestamps[-1]}'
