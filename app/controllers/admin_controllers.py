# app/controllers/admin_controller.py

import os
import logging
from flask import render_template, abort, send_file, request
from flask_login import login_required, current_user
from app import app

logger = logging.getLogger(__name__)

# Function to read log file and paginate log entries
def get_paginated_logs(page, per_page):
    log_file_path = os.environ.get('LOG_FILE') or 'app.log'
    try:
        with open(log_file_path, 'r') as log_file:
            log_entries = log_file.readlines()
            total_entries = len(log_entries)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_logs = log_entries[start:end]
            has_next = end < total_entries
            has_prev = start > 0
            return paginated_logs, has_next, has_prev
    except FileNotFoundError:
        logger.error(f"Log file not found: {log_file_path}")
        abort(500)

def parse_log_entry(log_entry):
    # Assuming CSV format: timestamp, level, message
    parts = log_entry.strip().split(',', 2)
    if len(parts) == 3:
        timestamp, level, message = parts
        return timestamp, level, message
    else:
        logger.warning(f"Invalid log entry format: {log_entry}")
        return "", "", log_entry  # Return placeholder values or handle as needed

def get_bootstrap_class(log_level):
    # Map log levels to Bootstrap classes
    level_class_mapping = {
        'DEBUG': 'table-info',
        'INFO': 'table-success',
        'WARNING': 'table-warning',
        'ERROR': 'table-danger',
        'CRITICAL': 'table-dark'
    }
    return level_class_mapping.get(log_level, '')

@app.route('/logs')
@login_required
def view_logs():
    if current_user.role != 'admin':
        logger.warning(f"Non-admin user {current_user.username} attempted to view logs.")
        abort(403)  # Only admins can view logs

    page = int(request.args.get('page', 1))
    per_page = 20  # Adjust as needed
    log_entries, has_next, has_prev = get_paginated_logs(page, per_page)

    parsed_entries = [parse_log_entry(entry) for entry in log_entries]

    entries_info = [parse_log_entry(entry) for entry in log_entries if 'INFO' in entry]
    entries_warning = [parse_log_entry(entry) for entry in log_entries if 'WARNING' in entry]
    entries_error = [parse_log_entry(entry) for entry in log_entries if 'ERROR' in entry]
    entries_debug = [parse_log_entry(entry) for entry in log_entries if 'DEBUG' in entry]
    entries_critical = [parse_log_entry(entry) for entry in log_entries if 'CRITICAL' in entry]

    logger.info(f"Admin user {current_user.username} viewed logs.")
    return render_template('admin/logs.html', entries_info=entries_info, entries_warning=entries_warning,
                           entries_error=entries_error, entries_debug=entries_debug,
                           entries_critical=entries_critical, has_next=has_next, has_prev=has_prev, page=page,
                           get_bootstrap_class=get_bootstrap_class)
