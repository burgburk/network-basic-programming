# import Libraries(Only pcapy used)
import pcapy

devices = pcapy.findalldevs()
   
# Ask user to choose the device name to sniff
print ("Available Network Interface Cards are\n ", devices)
dev = int(input("\nSelect Network Device (1 ~ {}) : ".format(len(devices))))-1
dev = devices[dev]
print ("\n", dev, "has Selected")

# Ask user to choose HTTP mode / DNS mode
tp = input("\nSelect HTTP/DNS (1: HTTP / 2: DNS) : ")
print()



# Parsing IP Header's Infomations from given packet
def getIPHeader(packet):
    IPHeader = {}
    IPHeader['IP_HL'] = int(bin(packet[14])[2:].zfill(8)[4:], 2)*4
    IPHeader['S_IP_Addr'] = "{}.{}.{}.{}".format(packet[26],packet[27],packet[28],packet[29])
    IPHeader['D_IP_Addr'] = "{}.{}.{}.{}".format(packet[30],packet[31],packet[32],packet[33])
    return IPHeader



# Parsing TCP Header's informations from given packet
def getTCPHeader(packet, start_index):
    TCPHeader = {}
    TCPHeader['S_Port'] = packet[start_index]*256+packet[start_index+1]
    TCPHeader['D_Port'] = packet[start_index+2]*256+packet[start_index+3]
    TCPHeader['Offset'] = int(bin(packet[start_index+12])[2:].zfill(8)[:4], 2)*4
    return TCPHeader



# Parsing UDP Header's informations from given packet
def getUDPHeader(packet, start_index):
    UDPHeader = {}
    UDPHeader['S_Port'] = packet[start_index]*256+packet[start_index+1]
    UDPHeader['D_Port'] = packet[start_index+2]*256+packet[start_index+3]
    return UDPHeader



# Parsing DNS Header's informations from given packet
def getDNSHeader(packet_without_header):
    DNSHeader = {}
    DNSHeader['ID'] = hex(packet_without_header[0]*256+packet_without_header[1])[2:]
    DNSHeader['QR'] = bin(packet_without_header[2])[2:].zfill(8)[0]
    DNSHeader['Opcode'] = bin(packet_without_header[2])[2:].zfill(8)[1:5]
    DNSHeader['AA'] = bin(packet_without_header[2])[2:].zfill(8)[5]
    DNSHeader['TC'] = bin(packet_without_header[2])[2:].zfill(8)[6]
    DNSHeader['RD'] = bin(packet_without_header[2])[2:].zfill(8)[7]
    DNSHeader['RA'] = bin(packet_without_header[3])[2:].zfill(8)[0]
    DNSHeader['Z'] = bin(packet_without_header[3])[2:].zfill(8)[1]
    DNSHeader['Rcode'] = bin(packet_without_header[3])[2:].zfill(8)[4:]
    DNSHeader['QDCOUNT'] = packet_without_header[4]*256+packet_without_header[5]
    DNSHeader['ANCOUNT'] = packet_without_header[6]*256+packet_without_header[7]
    DNSHeader['NSCOUNT'] = packet_without_header[8]*256+packet_without_header[9]
    DNSHeader['ARCOUNT'] = packet_without_header[10]*256+packet_without_header[11]
    return DNSHeader



# print HTTP Request/Response Header values using 'getXXXHeader' functions
def capture_HTTP(device_type):

    # Capture Packets Live & Filter HTTP
    cap = pcapy.open_live(dev, 65536 , 1 , 0)
    cap.setfilter('port 80')
    
    counter = 0

    while(1):
        # Capture next packet
        (header, packet) = cap.next()

        # Get IP Header Informations
        IPHeader = getIPHeader(packet)
        s_ip_addr, d_ip_addr= IPHeader['S_IP_Addr'], IPHeader['D_IP_Addr']

        # Get TCP Header Informations
        TCPHeader_startIndex = 14 + IPHeader['IP_HL']
        TCPHeader = getTCPHeader(packet, TCPHeader_startIndex)
        s_port, d_port= TCPHeader['S_Port'], TCPHeader['D_Port']

        # Decode Remaining Packets
        header_exitIndex = TCPHeader_startIndex + TCPHeader['Offset']
        packet_without_header = packet[header_exitIndex:]
        packet_decoded = packet_without_header.decode('ISO-8859-1') # 'ISO-8859-1'
        
        # Check if keyword 'HTTP' contained 
        if ('HTTP' in packet_decoded):

            # Check if packet includes Request Header, and print if included
            if ('GET' in packet_decoded) | ('POST' in packet_decoded) | ('PUT' in packet_decoded) | ('DELETE' in packet_decoded) | ('HEAD' in packet_decoded):
                counter+=1
                print("{} {}:{} {}:{} HTTP Request".format(counter, s_ip_addr, s_port, d_ip_addr, d_port))
                index = packet_decoded.index('\r\n\r\n')
                print(packet_decoded[:index] + '\n')

            # Check if packet includes Response Header, and print if included
            else:
                counter+=1
                print("{} {}:{} {}:{} HTTP Response".format(counter, s_ip_addr, s_port, d_ip_addr, d_port)) 
                index = packet_decoded.index('\r\n\r\n')                
                print(packet_decoded[:index] + '\n')

            


# print DNS Header values using 'getXXXHeader' functions
def capture_DNS(device_type):

    # Capture Packets Live & Filter DNS
    cap = pcapy.open_live(device_type, 65536 , 1 , 0)
    cap.setfilter('port 53')

    counter = 0

    while(1):
        # Capture next packet
        (header, packet) = cap.next()

        # Get IP Header Informations
        IPHeader = getIPHeader(packet)
        s_ip_addr, d_ip_addr= IPHeader['S_IP_Addr'], IPHeader['D_IP_Addr']

        # Get UDP Header Informations
        UDPHeader_startIndex = 14 + IPHeader['IP_HL']
        UDPHeader = getUDPHeader(packet, UDPHeader_startIndex)
        s_port, d_port= UDPHeader['S_Port'], UDPHeader['D_Port']

        # Decode Remaining Packets
        header_exitIndex = UDPHeader_startIndex + 8
        packet_without_header = packet[header_exitIndex:]
        packet_decoded = packet_without_header.decode('ISO-8859-1') # 'ISO-8859-1'
        
        # GET DNS Header Informations
        DNSHeader = getDNSHeader(packet_without_header)
        dns_id, qdcount, ancount, nscount, arcount = DNSHeader['ID'], DNSHeader['QDCOUNT'], DNSHeader['ANCOUNT'], DNSHeader['NSCOUNT'], DNSHeader['ARCOUNT']


        print("{} {}:{} {}:{} DNS ID : {}".format(counter, s_ip_addr, s_port, d_ip_addr, d_port, dns_id))
        print("{} | {} | {} | {} | {} | {} | {} | {}".format(DNSHeader['QR'], DNSHeader['Opcode'], DNSHeader['AA'], DNSHeader['TC'], DNSHeader['RD'], DNSHeader['RA'], DNSHeader['Z'], DNSHeader['Rcode']))
        print("QDCOUNT:{}\nANCOUNT:{}\nNSCOUNT:{}\nARCOUNT:{}\n".format(qdcount, ancount, nscount, arcount))

        counter+=1


        




# if User selects 1, call 'capture_HTTP' / if user selects 2, call 'capture_DNS' 
if (tp == '1'):
    capture_HTTP(dev)
elif (tp == '2'):
    capture_DNS(dev)