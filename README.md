# SupportOps Insight

Production support dashboard for analyzing application logs, identifying incidents, and generating structured incident reports.

## Features

- **Multi-format log parsing** — Standard, JSON, Syslog, and Simple formats
- **Log analysis dashboard** — Filter by severity, service, keywords; sort and paginate results
- **Error grouping** — Automatically groups repeated errors by message pattern
- **Severity classification** — Scores logs based on level, keywords, and critical services
- **Incident reports** — Professional HTML reports with print support
- **Reports management** — View and manage generated incident reports

## Requirements

- Python 3.8+
- pip

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Project Structure

```
supportops-insight/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── utils/
│   ├── log_parser.py           # Multi-format log parsing
│   ├── severity_classifier.py  # Error grouping and severity scoring
│   └── incident_generator.py   # HTML incident report generation
├── templates/                  # Jinja2 HTML templates
├── static/
│   ├── css/style.css           # Responsive styles
│   └── js/dashboard.js         # Frontend interactivity
├── uploads/                    # Uploaded log files (auto-created)
├── reports/                    # Generated incident reports (auto-created)
└── logs/                       # Application logs (auto-created)
```

## Usage

### 1. Upload Logs

1. Navigate to **Upload Logs**
2. Select one or more `.log`, `.txt`, or `.json` files (max 16MB each)
3. Click **Upload and Parse**

Sample test files are included in the project root:

- `sample_standard.log`
- `sample_json.log`
- `sample_syslog.log`

### 2. Analyze Logs

1. After upload, you are redirected to the analysis page
2. Use filters to narrow results by severity, service, or keyword
3. Review error groups sorted by frequency
4. Select log entries for incident reporting

**Keyboard shortcut:** `Ctrl+K` focuses the search box.

### 3. Generate Incident Reports

1. On the analysis page, select log entries (or use **Select Errors Only**)
2. Add optional notes
3. Click **Generate Report (Selected)** or **Generate Report (All Errors)**
4. View the report from the **Reports** page

## API Endpoint

```
GET /api/logs/<file_id>?level=ERROR&search=timeout&sort_by=timestamp&sort_order=desc
```

Returns JSON with parsed logs and error groups.

## Configuration

Environment variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key (required in production) |
| `FLASK_ENV` | `development` or `production` |

## Production Deployment

```bash
export SECRET_KEY="your-secure-secret-key"
export FLASK_ENV=production

pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Recommended:

- Use nginx as a reverse proxy
- Enable HTTPS with SSL certificates
- Set up log rotation for the `logs/` directory
- Back up `uploads/` and `reports/` folders regularly

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Upload fails | Check file extension (.log, .txt, .json) and size (max 16MB) |
| No logs parsed | Verify log format matches supported patterns |
| Empty analysis | Upload a file first from the Upload page |
| Reports not showing | Check the `reports/` directory exists and is writable |

## Manual Testing Checklist

- [ ] Upload single log file (all formats)
- [ ] Upload multiple log files at once
- [ ] Reject invalid file types
- [ ] Reject files over 16MB
- [ ] Filter logs by severity level
- [ ] Filter logs by service name
- [ ] Search logs by keyword
- [ ] Sort by timestamp and level
- [ ] Generate incident report with selected logs
- [ ] Generate incident report with all errors
- [ ] View generated reports list
- [ ] Delete uploaded log file
- [ ] Responsive design on mobile
- [ ] Print incident report

## License

MIT
