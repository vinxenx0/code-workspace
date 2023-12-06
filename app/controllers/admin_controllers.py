# app/controllers/admin_controller.py

import os
import logging
from flask import render_template, abort, send_file, request
from flask_login import login_required, current_user
from app import app

logger = logging.getLogger(__name__)

# Function to read log file and paginate log entries
def get_paginated_logs(page, per_page):
    log_file_path = os.environ.get('LOG_FILE') or 'logs/app.log' #hardcoded
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
    if current_user.role != 'superadmin':
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

# app/controllers/admin_controller.py

from flask import render_template, abort, request
from flask_login import login_required, current_user
from app import app

# ... existing code ...

def get_web_status():
    # Simulate web status (replace with actual web status logic)
    return "OK"

def get_network_info():
    # Simulate network info (replace with actual network info logic)
    return "Network status: OK"

def get_storage_info():
    # Simulate storage info (replace with actual storage info logic)
    used_space = "50 GB"  # Replace with actual used space
    free_space = "100 GB"  # Replace with actual free space
    return f"Used space: {used_space}, Free space: {free_space}"

@app.route('/system')
@login_required
def view_system():
    if current_user.role != 'superadmin':
        abort(403)  # Only admins can view system info

    web_status = get_web_status()
    network_info = get_network_info()
    storage_info = get_storage_info()
    logs = get_system_logs()

    return render_template('admin/system.html', web_status=web_status, network_info=network_info, storage_info=storage_info, logs=logs)


def get_web_status():
    # Simulate web status (replace with actual web status logic)
    return "OK"

def get_network_info():
    # Simulate network info (replace with actual network info logic)
    return "Network status: OK"

def get_storage_info():
    # Simulate storage info (replace with actual storage info logic)
    used_space = "50 GB"  # Replace with actual used space
    free_space = "100 GB"  # Replace with actual free space
    return f"Used space: {used_space}, Free space: {free_space}"

def get_system_logs():
    # Simulate system logs (replace with actual system logs retrieval logic)
    system_logs = [
        '2023-11-30 10:15:20, ERROR, System error 1',
        '2023-11-30 10:20:30, WARNING, System warning 1',
        '2023-11-30 11:05:45, ERROR, System error 2',
    ]
    return [parse_log_entry(entry) for entry in system_logs]