import wmi
def test_wmi_connection(computer, user, password):

    try:
        connection = wmi.WMI(computer=computer, user=user, password=password)
        print(f"Successfully connected to {computer}")
        return connection
    except wmi.x_wmi as e:
        print(f"Failed to connect to {computer}: {str(e)}")
        return None
    
    
