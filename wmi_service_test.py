import wmi

def get_running_services(computer, user, password):
    try:
        # Connect to the remote WMI service
        connection = wmi.WMI(computer=computer, user=user, password=password)
        print(f"Successfully connected to {computer}")

        # Get details about running services
        running_services = []
        for service in connection.Win32_Service(Name="OracleServiceMGOLD"):
            running_services.append({
                "name": service.Name,
                "display_name": service.DisplayName,
                "status": service.Status,
            })

        # Print details about each running service
        for service in running_services:
            print(f"Service Name: {service['name']}")
            print(f"Display Name: {service['display_name']}")
            print(f"Status: {service['status']}")
            print("-" * 50)

        return running_services
    except wmi.x_wmi as e:
        print(f"Failed to connect to {computer}: {str(e)}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None

# Replace with your remote machine's details
get_running_services("IP", "user", "password")
