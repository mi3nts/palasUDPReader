import socket
import datetime
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
        print(type(data))
        print(type(print(type(data))))
        # Step 2: Split by semicolons to get key-value pairs

        # message = str(data)
        # # Step 1: Extract the portion after 'sendVal'
        # start = message.find('<sendVal ') + len('<sendVal ')
        # end = message.find('>', start)
        # data_str = message[start:end]
        # key_value_pairs = data_str.split(';')

        # # Step 3: Split each pair into key and value, and store in a dictionary
        # data_dict = {}
        # for pair in key_value_pairs:
        #     if '=' in pair:
        #         key, value = pair.split('=')
        #         data_dict[int(key)] = float(value)

        # # Step 4: Print the decoded dictionary
        # print(data_dict)
        # buffer_size = len(data)
        # print(data[0])
        # print(f"Buffer size of received message: {buffer_size} bytes")
    except Exception as e:
        print(f"Error receiving data: {e}")
