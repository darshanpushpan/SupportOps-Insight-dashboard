/**
 * SupportOps Insight - Dashboard JavaScript
 * Frontend functionality for log analysis and incident reporting
 */

document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });

    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
});

function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

function toggleSelectAll(source) {
    const checkboxes = document.querySelectorAll('input[name="logs"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.checked = source.checked;
    });
}

function selectErrorsOnly() {
    const checkboxes = document.querySelectorAll('input[name="logs"]');
    checkboxes.forEach(function(checkbox) {
        const row = checkbox.closest('tr');
        if (!row) return;
        const levelCell = row.querySelectorAll('td')[2];
        if (!levelCell) return;
        const level = levelCell.textContent.trim().toUpperCase();
        checkbox.checked = (level === 'ERROR' || level === 'CRITICAL');
    });
}

function clearFilters() {
    const form = document.getElementById('filter-form') || document.querySelector('form[method="GET"]');
    if (form) {
        form.reset();
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(function(input) {
            if (input.type === 'text' || input.tagName === 'SELECT') {
                input.value = '';
            }
        });
        form.submit();
    }
}

function exportLogsAsCSV() {
    const table = document.getElementById('logs-table');
    if (!table) {
        alert('No logs to export');
        return;
    }

    const csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(function(col, index) {
            if (index === 0 || index === cols.length - 1) {
                return;
            }
            rowData.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
        });
        if (rowData.length) {
            csv.push(rowData.join(','));
        }
    });

    const csvString = csv.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'logs_' + new Date().toISOString().slice(0, 10) + '.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

let searchTimeout;
function debounceSearch(input) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(function() {
        input.closest('form').submit();
    }, 500);
}

function filterByLevel(level) {
    const rows = document.querySelectorAll('#logs-table tbody tr');
    rows.forEach(function(row) {
        const levelCell = row.querySelectorAll('td')[2];
        if (!levelCell) return;
        const rowLevel = levelCell.textContent.trim().toUpperCase();
        row.style.display = (level === '' || rowLevel === level) ? '' : 'none';
    });
}

function highlightSearchTerm(term) {
    if (!term) return;

    const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp('(' + escaped + ')', 'gi');
    const messageCells = document.querySelectorAll('#logs-table td:nth-child(6)');

    messageCells.forEach(function(cell) {
        const text = cell.textContent;
        cell.innerHTML = text.replace(regex, '<mark>$1</mark>');
    });
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Copied to clipboard!');
    }).catch(function(err) {
        console.error('Failed to copy: ', err);
    });
}

function updateFileInput(input) {
    const fileName = input.parentElement.querySelector('.file-name');
    if (input.files && input.files.length > 0) {
        const names = Array.from(input.files).map(function(f) { return f.name; }).join(', ');
        fileName.textContent = names.length > 80 ? names.substring(0, 80) + '...' : names;
        fileName.style.color = '#333';
        fileName.style.fontWeight = '600';
    } else {
        fileName.textContent = 'No files selected';
        fileName.style.color = '#666';
        fileName.style.fontWeight = 'normal';
    }
}

function validateUploadForm() {
    const fileInput = document.getElementById('files');
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert('Please select at least one file to upload');
        return false;
    }

    const allowedExtensions = ['log', 'txt', 'json'];
    const maxSize = 16 * 1024 * 1024;

    for (let i = 0; i < fileInput.files.length; i++) {
        const file = fileInput.files[i];
        const extension = file.name.split('.').pop().toLowerCase();

        if (allowedExtensions.indexOf(extension) === -1) {
            alert('File "' + file.name + '" has an invalid extension. Allowed: .log, .txt, .json');
            return false;
        }

        if (file.size > maxSize) {
            alert('File "' + file.name + '" exceeds the maximum size of 16MB');
            return false;
        }
    }

    return true;
}

const levelColors = {
    'DEBUG': '#6c757d',
    'INFO': '#28a745',
    'WARNING': '#ffc107',
    'ERROR': '#fd7e14',
    'CRITICAL': '#dc3545'
};

function getLevelColor(level) {
    return levelColors[level.toUpperCase()] || '#6c757d';
}

function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function timeAgo(timestamp) {
    if (!timestamp) return '';
    const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return Math.floor(seconds / 60) + ' minutes ago';
    if (seconds < 86400) return Math.floor(seconds / 3600) + ' hours ago';
    return Math.floor(seconds / 86400) + ' days ago';
}
