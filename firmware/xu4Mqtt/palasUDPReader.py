import socket
import datetime

import pandas as pd

# Define the data as lists
data = {
    "Data channel": list(range(110, 205)),
    "Xlower [µm]": [0.100000, 0.107461, 0.115478, 0.124094, 0.133352, 0.143301, 0.153993, 0.165482, 
                    0.177828, 0.191095, 0.205353, 0.220673, 0.237137, 0.254830, 0.273842, 0.294273,
                    0.316228, 0.339821, 0.365174, 0.392419, 0.421697, 0.453158, 0.486968, 0.523299,
                    0.562341, 0.604296, 0.649382, 0.697831, 0.749894, 0.805842, 0.865964, 0.930572,
                    1.000000, 1.074608, 1.154782, 1.240938, 1.333521, 1.433013, 1.539927, 1.654817, 
                    1.778279, 1.910953, 2.053525, 2.206734, 2.371374, 2.548297, 2.738420, 2.942727, 
                    3.162278, 3.398208, 3.651741, 3.924190, 4.216965, 4.531584, 4.869675, 5.232991],
    "Xupper [µm]": [0.107461, 0.115478, 0.124094, 0.133352, 0.143301, 0.153993, 0.165482, 0.177828,
                    0.191095, 0.205353, 0.220673, 0.237137, 0.254830, 0.273842, 0.294273, 0.316228,
                    0.339821, 0.365174, 0.392419, 0.421697, 0.453158, 0.486968, 0.523299, 0.562341,
                    0.604296, 0.649382, 0.697831, 0.749894, 0.805842, 0.865964, 0.930572, 1.000000,
                    1.074608, 1.154782, 1.240938, 1.333521, 1.433013, 1.539927, 1.654817, 1.778279,
                    1.910953, 2.053525, 2.206734, 2.371374, 2.548297, 2.738420, 2.942727, 3.162278,
                    3.398208, 3.651741, 3.924190, 4.216965, 4.531584, 4.869675, 5.232991, 5.623413,
                    6.042964, 6.493816, 6.978306, 7.498942, 8.058422, 8.659643, 9.305720, 10.000000,
                    10.746078, 11.547820, 12.409378, 13.335215, 14.330126, 15.399265, 16.548170, 
                    17.782795, 19.109529, 20.535250, 22.067341, 23.713737, 25.482967, 27.384197,
                    29.427271, 31.622776, 33.982082, 36.517414, 39.241898, 42.169651, 45.315838,
                    48.696751, 52.329910, 56.234131, 60.429638, 64.938164, 69.783058, 74.989418,
                    80.584221, 86.596436, 93.057205]
}

# Create DataFrame
df = pd.DataFrame(data)

print(df)
# # Add 'Midpoint [µm]' column
# df['Midpoint [µm]'] = (df['Xlower [µm]'] + df['Xupper [µm]']) / 2

# # Print the updated DataFrame
# print(df)



# Set up the UDP socket
UDP_IP = "0.0.0.0"  # Listen on all network interfaces
UDP_PORT = 56790     # Set the port number you're expecting (e.g., 5005)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP data on port {UDP_PORT}...")

while True:
    try:
        # Using a large buffer size to handle unknown packet size (max 65507 for UDP)
        print(datetime.datetime.now())
        data, addr = sock.recvfrom(2000)  # Maximum possible UDP packet size
        print(f"Received message from {addr}: {data.decode('ascii', errors='ignore')}")

        message = data.decode('ascii', errors='ignore')

        # # Step 1: Extract the portion after 'sendVal'
        start = message.find('<sendVal ') + len('<sendVal ')
        end = message.find('>', start)
        data_str = message[start:end]
        key_value_pairs = data_str.split(';')

        # Step 3: Split each pair into key and value, and store in a dictionary
        data_dict = {}
        for pair in key_value_pairs:
            if '=' in pair:
                key, value = pair.split('=')
                data_dict[int(key)] = float(value)

        # Step 4: Print the decoded dictionary
        print(data_dict)
        buffer_size = len(data)
        print(data[0])
        print(f"Buffer size of received message: {buffer_size} bytes")

    except Exception as e:
        print(f"Error receiving data: {e}")
