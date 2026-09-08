"""Multi-format log parsing logic for SupportOps Insight."""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil import parser as date_parser


class LogParser:
    """Parse log files in multiple formats and normalize entries."""

    STANDARD_PATTERN = re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+'
        r'\[(?P<service>[^\]]+)\]\s+'
        r'\[(?P<host>[^\]]+)\]\s+'
        r'(?P<message>.+)$',
        re.IGNORECASE,
    )

    SYSLOG_PATTERN = re.compile(
        r'^(?P<syslog_ts>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<host>\S+)\s+\S+:\s+'
        r'(?P<message>.+)$'
    )

    SIMPLE_COLON_PATTERN = re.compile(
        r'^(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL):\s*(?P<message>.+)$',
        re.IGNORECASE,
    )

    SIMPLE_BRACKET_PATTERN = re.compile(
        r'^\[(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\]\s*(?P<message>.+)$',
        re.IGNORECASE,
    )

    LEVEL_IN_MESSAGE_PATTERN = re.compile(
        r'\[(?P<level>debug|info|warning|error|critical|err|warn)\]',
        re.IGNORECASE,
    )

    VALID_LEVELS = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}

    def __init__(self):
        """Initialize the log parser."""
        self._entry_counter = 0

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse an entire log file and return normalized log entries.

        Args:
            file_path: Path to the log file on disk.

        Returns:
            List of parsed log entry dictionaries.
        """
        entries: List[Dict[str, Any]] = []
        self._entry_counter = 0

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as handle:
                for line_number, line in enumerate(handle, start=1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    entry = self.parse_line(stripped, line_number)
                    if entry:
                        entries.append(entry)
        except OSError as exc:
            raise ValueError(f'Unable to read log file: {exc}') from exc

        return entries

    def parse_line(self, line: str, line_number: int = 1) -> Optional[Dict[str, Any]]:
        """
        Parse a single log line, auto-detecting the format.

        Args:
            line: Raw log line text.
            line_number: Line number in the source file.

        Returns:
            Parsed log entry dictionary or None if parsing fails.
        """
        entry = (
            self._parse_json(line)
            or self._parse_standard(line)
            or self._parse_syslog(line)
            or self._parse_simple(line)
        )

        if not entry:
            return None

        self._entry_counter += 1
        entry['id'] = f'log_{self._entry_counter}'
        entry['line_number'] = line_number
        entry['raw'] = line
        entry['level'] = entry.get('level', 'INFO').upper()
        entry['service'] = entry.get('service') or 'Unknown'
        entry['host'] = entry.get('host') or 'Unknown'
        entry['parsed_timestamp'] = self._normalize_timestamp(entry.get('timestamp'))

        return entry

    def detect_format(self, sample_lines: List[str]) -> str:
        """
        Detect the dominant log format from sample lines.

        Args:
            sample_lines: List of raw log lines.

        Returns:
            Format name: json, standard, syslog, simple, or unknown.
        """
        scores = {'json': 0, 'standard': 0, 'syslog': 0, 'simple': 0}

        for line in sample_lines[:20]:
            stripped = line.strip()
            if not stripped:
                continue
            if self._parse_json(stripped):
                scores['json'] += 1
            elif self.STANDARD_PATTERN.match(stripped):
                scores['standard'] += 1
            elif self.SYSLOG_PATTERN.match(stripped):
                scores['syslog'] += 1
            elif self._parse_simple(stripped):
                scores['simple'] += 1

        best_format = max(scores, key=scores.get)
        return best_format if scores[best_format] > 0 else 'unknown'

    def _parse_json(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse JSON-formatted log lines."""
        if not line.startswith('{'):
            return None

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        timestamp = data.get('timestamp') or data.get('time') or data.get('@timestamp')
        level = str(data.get('level') or data.get('severity') or 'INFO').upper()
        message = data.get('message') or data.get('msg') or json.dumps(data)
        service = data.get('service') or data.get('app') or data.get('logger')
        host = data.get('host') or data.get('hostname') or data.get('server')

        return {
            'timestamp': str(timestamp) if timestamp else None,
            'level': level if level in self.VALID_LEVELS else 'INFO',
            'service': service,
            'host': host,
            'message': str(message),
        }

    def _parse_standard(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse standard application log format."""
        match = self.STANDARD_PATTERN.match(line)
        if not match:
            return None

        groups = match.groupdict()
        return {
            'timestamp': groups['timestamp'],
            'level': groups['level'].upper(),
            'service': groups['service'],
            'host': groups['host'],
            'message': groups['message'],
        }

    def _parse_syslog(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse syslog-style log lines."""
        match = self.SYSLOG_PATTERN.match(line)
        if not match:
            return None

        groups = match.groupdict()
        message = groups['message']
        level = self._extract_level_from_message(message)
        timestamp = self._parse_syslog_timestamp(groups['syslog_ts'])

        return {
            'timestamp': timestamp or groups['syslog_ts'],
            'level': level,
            'service': 'Unknown',
            'host': groups['host'],
            'message': message,
        }

    def _parse_simple(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse simple ERROR: or [ERROR] log formats."""
        match = self.SIMPLE_COLON_PATTERN.match(line) or self.SIMPLE_BRACKET_PATTERN.match(line)
        if not match:
            return None

        groups = match.groupdict()
        return {
            'timestamp': None,
            'level': groups['level'].upper(),
            'service': 'Unknown',
            'host': 'Unknown',
            'message': groups['message'],
        }

    def _extract_level_from_message(self, message: str) -> str:
        """Extract log level from syslog message content."""
        match = self.LEVEL_IN_MESSAGE_PATTERN.search(message)
        if not match:
            return 'INFO'

        level = match.group('level').upper()
        mapping = {'ERR': 'ERROR', 'WARN': 'WARNING'}
        level = mapping.get(level, level)
        return level if level in self.VALID_LEVELS else 'INFO'

    def _parse_syslog_timestamp(self, syslog_ts: str) -> Optional[str]:
        """Convert syslog timestamp to ISO format using current year."""
        try:
            current_year = datetime.now().year
            parsed = date_parser.parse(f'{syslog_ts} {current_year}')
            return parsed.isoformat()
        except (ValueError, OverflowError):
            return None

    def _normalize_timestamp(self, timestamp: Optional[str]) -> Optional[str]:
        """Normalize timestamp strings to ISO format."""
        if not timestamp:
            return None

        try:
            parsed = date_parser.parse(str(timestamp))
            return parsed.isoformat()
        except (ValueError, OverflowError, TypeError):
            return str(timestamp)
