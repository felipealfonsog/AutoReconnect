import subprocess
import time
import re

def get_current_service():
    result = subprocess.run(['connmanctl', 'services'], capture_output=True, text=True)
    services = result.stdout.splitlines()
    for service in services:
        if 'Connected' in service:
            return re.search(r'(\S+)', service).group(1)
    return None

def get_available_services():
    result = subprocess.run(['connmanctl', 'services'], capture_output=True, text=True)
    services = result.stdout.splitlines()
    available_services = []
    for service in services:
        if 'WiFi' in service and 'Connected' not in service:
            available_services.append(re.search(r'(\S+)', service).group(1))
    return available_services

def connect_to_service(service):
    subprocess.run(['connmanctl', 'connect', service])

def disconnect_from_service(service):
    subprocess.run(['connmanctl', 'disconnect', service])

def check_internet():
    result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True)
    return result.returncode == 0

def main():
    previous_service = get_current_service()
    
    while True:
        current_service = get_current_service()
        if not current_service:
            if previous_service:
                disconnect_from_service(previous_service)
            services = get_available_services()
            if services:
                connect_to_service(services[0])
                time.sleep(10)  # Wait to establish connection
                if not check_internet():
                    disconnect_from_service(services[0])
                else:
                    previous_service = services[0]
        else:
            previous_service = current_service

        time.sleep(30)  # Check every 30 seconds

if __name__ == '__main__':
    main()
