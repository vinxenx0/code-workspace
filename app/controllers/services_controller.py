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
    global SERVICE_STATES

    if service_name in SERVICE_STATES:
        current_state = SERVICE_STATES[service_name]

        if current_state == 'active':
            SERVICE_STATES[service_name] = 'inactive'
            stop_service(service_name)
        else:
            SERVICE_STATES[service_name] = 'active'
            start_service(service_name)

        return jsonify({'status': 'success', 'state': SERVICE_STATES[service_name]})
    else:
        return jsonify({'status': 'error', 'message': 'Unknown Service'})

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




def start_service(service_name):
    # Add logic to start the specified service
    # You might need to adjust this based on your system configuration
    pass

def stop_service(service_name):
    # Add logic to stop the specified service
    # You might need to adjust this based on your system configuration
    pass


def check_service_status(service_name):
    # Use system commands to check the status of the services
    # You might need to adjust these commands based on your system configuration
    if service_name == 'web_server':
        return check_web_server_status()
    elif service_name == 'dns_resolver':
        return check_dns_resolver_status()
    else:
        return 'Unknown Service'

