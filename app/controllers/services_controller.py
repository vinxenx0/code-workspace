# app/controllers/services_controller.py

from flask import render_template, jsonify
from flask_login import login_required
from app import app

# Define service states
SERVICE_STATES = {'web_server': 'active', 'dns_resolver': 'inactive'}


@app.route('/services')
@login_required
def services():
    # Check the status of the services (you may need to adjust the commands based on your system)
    web_status = check_service_status('web_server')
    dns_status = check_service_status('dns_resolver')

    return render_template('services/index.html', web_status=web_status, dns_status=dns_status, SERVICE_STATES=SERVICE_STATES)


@app.route('/toggle_service/<service_name>', methods=['POST'])
@login_required
def toggle_service(service_name):
    return jsonify(toggle_service_status(service_name))

def toggle_service_status(service_name):
    global SERVICE_STATES

    if service_name in SERVICE_STATES:
        current_state = SERVICE_STATES[service_name]

        if current_state == 'active':
            SERVICE_STATES[service_name] = 'inactive'
            return stop_service(service_name)
        else:
            SERVICE_STATES[service_name] = 'active'
            return start_service(service_name)
    else:
        return {'status': 'error', 'message': 'Unknown Service'}

def check_service_status(service_name):
    # Use system commands to check the status of the services
    # You might need to adjust these commands based on your system configuration
    if service_name == 'web_server':
        return check_web_server_status()
    elif service_name == 'dns_resolver':
        return check_dns_resolver_status()
    else:
        return 'Unknown Service'

def check_web_server_status():
    # Example: Check if the web server is running on port 5000
    # You might need to adjust this command based on your web server configuration
    command = "nc -zv localhost 5000"
    return execute_command(command)

def check_dns_resolver_status():
    # Example: Check if DNS resolver is reachable
    # You might need to adjust this command based on your DNS resolver configuration
    command = "nslookup google.com"
    return execute_command(command)

def execute_command(command):
    # Helper function to execute system commands
    import subprocess
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 'Running'  # Return a string indicating the service is running
    except subprocess.CalledProcessError as e:
        return 'Stopped'  # Return a string indicating the service is stopped


def start_web_server():
    # Logic to start the web server
    pass

def stop_web_server():
    # Logic to stop the web server
    pass 

def start_dns_resolver():
    # Logic to start the DNS resolver
    pass

def stop_dns_resolver():
    # Logic to stop the DNS resolver
    pass

def start_email_service():
    # Logic to start the email service
    pass

def stop_email_service():
    # Logic to stop the email service
    pass

def start_task_scheduler():
    # Logic to start the task scheduler
    pass

def stop_task_scheduler():
    # Logic to stop the task scheduler
    pass

def start_notification_service():
    # Logic to start the notification service
    pass

def stop_notification_service():
    # Logic to stop the notification service
    pass

def start_file_processor():
    # Logic to start the file processor
    pass

def stop_file_processor():
    # Logic to stop the file processor
    pass

def start_database_cleaner():
    # Logic to start the database cleaner
    pass

def stop_database_cleaner():
    # Logic to stop the database cleaner
    pass

def start_service(service_name):
    if service_name == 'web_server':
        start_web_server()
    elif service_name == 'dns_resolver':
        start_dns_resolver()
    elif service_name == 'email_service':
        start_email_service()
    elif service_name == 'task_scheduler':
        start_task_scheduler()
    elif service_name == 'notification_service':
        start_notification_service()
    elif service_name == 'file_processor':
        start_file_processor()
    elif service_name == 'database_cleaner':
        start_database_cleaner()
    # Add more services as needed

    return {'status': 'success', 'state': 'Running'}

def stop_service(service_name):
    if service_name == 'web_server':
        stop_web_server()
    elif service_name == 'dns_resolver':
        stop_dns_resolver()
    elif service_name == 'email_service':
        stop_email_service()
    elif service_name == 'task_scheduler':
        stop_task_scheduler()
    elif service_name == 'notification_service':
        stop_notification_service()
    elif service_name == 'file_processor':
        stop_file_processor()
    elif service_name == 'database_cleaner':
        stop_database_cleaner()
    # Add more services as needed

    return {'status': 'success', 'state': 'Stopped'}