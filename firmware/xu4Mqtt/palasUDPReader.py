import socket
import datetime
import time
# Set up the UDP socket
UDP_IP = "0.0.0.0"  # Listen on all network interfaces
UDP_PORT = 56790     # Set the port number you're expecting (e.g., 5005)

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# print(f"Listening for UDP data on port {UDP_PORT}...")

while True:
    try:
        # Using a large buffer size to handle unknown packet size (max 65507 for UDP)
        print(datetime.datetime.now())
        # data, addr = sock.recvfrom(2000)  # Maximum possible UDP packet size
        # print(data)
        time.sleep(1)
        # print(data.decode('ascii', errors='ignore'))
        # # Calculate buffer size
        # buffer_size = len(data)
        # print(data)
        # print(f"Buffer size of received message: {buffer_size} bytes")
    except Exception as e:
        print(e)
