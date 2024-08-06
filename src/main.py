import subprocess
import time

def get_connected_service():
    """Get the currently connected WiFi service."""
    try:
        result = subprocess.run(['connmanctl', 'services'], capture_output=True, text=True)
        services = result.stdout.splitlines()
        for line in services:
            if line.startswith('*'):
                # Extract the full service identifier
                parts = line.split()
                service = parts[-1]
                return service
    except Exception as e:
        print(f"Error getting connected service: {e}")
    return None

def get_available_services():
    """Get a list of all available WiFi services."""
    try:
        result = subprocess.run(['connmanctl', 'services'], capture_output=True, text=True)
        services = result.stdout.splitlines()
        available_services = []
        for line in services:
            if not line.startswith('*') and 'wifi' in line:
                parts = line.split()
                service = parts[-1]
                available_services.append(service)
        return available_services
    except Exception as e:
        print(f"Error getting available services: {e}")
    return []

def connect_service(service):
    """Connect to a specified WiFi service using its full identifier."""
    print(f"Attempting to connect to {service}")
    try:
        subprocess.run(['connmanctl', 'connect', service], check=True)
        print(f"Connected to {service}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect to {service}: {e}")
        return False

def disconnect_service(service):
    """Disconnect from a specified WiFi service using its full identifier."""
    print(f"Attempting to disconnect from {service}")
    try:
        subprocess.run(['connmanctl', 'disconnect', service], check=True)
        print(f"Disconnected from {service}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to disconnect from {service}: {e}")

def restart_connman():
    """Restart the ConnMan service."""
    print("Restarting ConnMan service...")
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'connman'], check=True)
        print("ConnMan service restarted.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart ConnMan service: {e}")

def is_internet_connected():
    """Check if the system is connected to the Internet."""
    try:
        result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking Internet connection: {e}")
    return False

def monitor_wifi():
    """Monitor WiFi connection status and reconnect if disconnected or move to the next network."""
    connected_service = get_connected_service()
    if connected_service is None:
        print("No WiFi service is currently connected.")
        return

    print(f"Currently connected to: {connected_service}")

    while True:
        time.sleep(10)  # Check every 10 seconds
        current_service = get_connected_service()

        if current_service != connected_service:
            print("Disconnected or connected to a different network.")
            connected_service = current_service  # Update the current connected service

        if not is_internet_connected():
            print("Internet connection lost. Attempting to reconnect.")
            disconnect_service(connected_service)
            
            if not connect_service(connected_service):
                print("Failed to reconnect to the previous network. Trying the next available network.")
                available_services = get_available_services()
                
                if available_services:
                    # Remove the current service from the list if present
                    if connected_service in available_services:
                        available_services.remove(connected_service)
                    
                    # Try connecting to the next available service
                    for service in available_services:
                        if connect_service(service):
                            connected_service = service
                            break
                else:
                    print("No other WiFi networks available to connect.")
                    # Restart ConnMan service if still no internet
                    restart_connman()
                    time.sleep(30)  # Wait a bit after restarting ConnMan
                    # Retry connection after restarting ConnMan
                    connected_service = get_connected_service()
                    if connected_service:
                        connect_service(connected_service)

if __name__ == "__main__":
    monitor_wifi()
