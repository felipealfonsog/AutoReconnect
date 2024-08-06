import subprocess
import time

def get_services():
    try:
        output = subprocess.check_output(["connmanctl", "services"], text=True)
        return output
    except subprocess.CalledProcessError as e:
        print("Failed to get services:", e)
        return None

def extract_services(output):
    services = []
    for line in output.splitlines():
        if 'wifi_' in line:
            parts = line.split()
            if len(parts) > 0:
                service_id = parts[0].strip('*')
                readable_ssid = ' '.join(parts[1:])
                services.append((service_id, readable_ssid))
    return services

def get_saved_networks():
    services_output = get_services()
    if services_output:
        return extract_services(services_output)
    return []

def is_connected():
    services_output = get_services()
    if services_output:
        for line in services_output.splitlines():
            if '*' in line:
                parts = line.split()
                if len(parts) > 0:
                    service_id = parts[0].strip('*')
                    readable_ssid = ' '.join(parts[1:])
                    return (service_id, readable_ssid)
    return (None, None)

def connect_to_network(service_id):
    print(f"Attempting to connect to {service_id}...")
    try:
        # Attempting to connect with the full service_id
        result = subprocess.run(["connmanctl", "connect", service_id], capture_output=True, text=True)
        print(f"Output of connect attempt:\n{result.stdout.strip()}\n{result.stderr.strip()}")

        if result.returncode == 0:
            # Check connection status
            time.sleep(10)
            connected_service_id, _ = is_connected()
            if connected_service_id == service_id:
                print(f"Successfully connected to {service_id}.")
                return True
            else:
                print(f"Failed to connect to {service_id}.")
                return False
        else:
            print(f"Error connecting to {service_id}: {result.stderr.strip()}")
            return False
    except subprocess.CalledProcessError as e:
        print("Failed to connect:", e)
        return False

def check_internet():
    try:
        subprocess.check_call(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("Checking initial connection...")
    connected_service_id, connected_ssid = is_connected()
    
    if connected_service_id:
        print(f"Initial connection: {connected_ssid} ({connected_service_id})")
    else:
        print("No initial connection. Scanning for networks...")

    internet_connected = False

    while True:
        if not check_internet():
            print("No internet connection. Trying to reconnect to the last known network...")
            if connected_service_id:
                if connect_to_network(connected_service_id):
                    time.sleep(10)
                    if check_internet():
                        print("Connected to the internet.")
                        internet_connected = True
                    else:
                        print(f"Failed to reconnect to {connected_service_id}. Trying other saved networks...")
                        saved_networks = get_saved_networks()
                        
                        if saved_networks:
                            for service_id, ssid in saved_networks:
                                if service_id != connected_service_id:
                                    print(f"Attempting to connect to {service_id}...")
                                    if connect_to_network(service_id):
                                        time.sleep(10)
                                        
                                        if check_internet():
                                            print("Connected to the internet.")
                                            internet_connected = True
                                            connected_service_id = service_id
                                            connected_ssid = ssid
                                            break
                                        else:
                                            print(f"Failed to connect to {service_id}")
                        else:
                            print("No saved networks available to connect.")
            else:
                print("No saved network available to reconnect. Trying again...")
            
            if not internet_connected:
                print("Still no internet. Trying again...")
                time.sleep(10)
                
        else:
            if not internet_connected:
                print("Connected to the internet.")
                internet_connected = True
            
            connected_service_id, connected_ssid = is_connected()
            time.sleep(10)

if __name__ == "__main__":
    main()
