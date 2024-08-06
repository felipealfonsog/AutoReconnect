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
                # The full identifier is the last part in the line
                service = parts[-1]
                return service
    except Exception as e:
        print(f"Error getting connected service: {e}")
    return None

def connect_service(service):
    """Connect to a specified WiFi service using its full identifier."""
    try:
        subprocess.run(['connmanctl', 'connect', service], check=True)
        print(f"Attempting to connect to {service}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect to {service}: {e}")

def disconnect_service(service):
    """Disconnect from a specified WiFi service using its full identifier."""
    try:
        subprocess.run(['connmanctl', 'disconnect', service], check=True)
        print(f"Disconnected from {service}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to disconnect from {service}: {e}")

def is_internet_connected():
    """Check if the system is connected to the Internet."""
    try:
        result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking Internet connection: {e}")
    return False

def monitor_wifi():
    """Monitor WiFi connection status and reconnect if disconnected."""
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
            # Try to reconnect to the previously connected service
            connect_service(connected_service)
            connected_service = get_connected_service()  # Update current service
        else:
            # Check if we have Internet connection
            if not is_internet_connected():
                print("Internet connection lost. Attempting to reconnect.")
                disconnect_service(connected_service)
                connect_service(connected_service)
        
if __name__ == "__main__":
    monitor_wifi()
