import socket
import select
import errno
from Printer import Printer
from DataCollector import DataCollector
# from CallsignRequester import CallsignRequester

#Well, that's all folks!
#TODO: Use .strip (or is it .split?) to look for printers to print to. 
#TODO: Add logic to subscribe/remove printers to print to
#TODO: Transmit GI messages
#TODO: When a printer is added, print a strip at the recieving end indicating operational status.

#old todo that isn't up to date
#TODO: Add logic to connect to server if it isn't "this" machine.
#TODO: Add logic to process printer connecting/unresponsive(disconnect) to server.
#TODO: Process "send strip to departure" message.
#TODO EVENTUALLY: Store times on here lol.

class Network():
    def __init__(self, user_position, control_area:str, printer:Printer, data_collector:DataCollector) -> None:
        self.debug_mode = True #For dev work... lol
        self.Privacy_mode = False
        #config initalization
        self.control_area = control_area
        self.user_position = user_position
        self.printer = printer
        self.data_collector = data_collector
        #Config network data.
        self.is_server_host = False
        self.network_active = False
        self.server_port = 9511
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.header_len = 8
        if self.debug_mode: print(f"Header length is set to {self.header_len}.")
        self.network_devices = dict() #This is a list of all available "devices" on our server. Really, it should just list each position thats connected.
        self.target_machines = set()  #This is a list of printers that we want our strips to go out to.

    def initialize_networking(self):
        print("Initializing electronic flight strip transfer system configurator...")
        #Determine "where" server is.
        self.server_ip = ""
        self.server_ip = input("Please input the IP of the server. Leave blank if this machine is the server: ")
        self.server_ip = self.server_ip.strip()
        if self.server_ip == "":
            self.server_ip = socket.gethostbyname(socket.getfqdn())
            self.is_server_host = True
        if self.Privacy_mode == False: #Privacy Mode is only togglable in this file. If its DISABLED, it should show the user their IP and PORT so that other machines can connect.
            print(f"Server IP set to {self.server_ip}. Port number {self.server_port}.")
        return self.is_server_host

    def run_server(self): #https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
        #try:  #This logic is flawed (it throws an error and then continues to attempt the server lol)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.server_ip, self.server_port)) #advises local OS that this particular IP and PORT are in use.
        self.socket.listen()
        if self.debug_mode: print(f"Server running.")
        self.sockets_list = [self.socket]
        # except:
        #   print("Unable to initialize server.")

        while True:
            read_socket, _, exception_socket = select.select(self.sockets_list, [], self.sockets_list)
            if self.debug_mode: print(f"READ {read_socket} & EXCEPT {exception_socket}")
            if self.debug_mode: print(f"Someone is accessing the server.")
            for notified_socket in read_socket:
                if notified_socket == self.socket: #New connection!
                    client_socket, client_addy = self.socket.accept()
                    if self.debug_mode: print(f"Client {client_socket} connection accepted.")
                    #Station should report name on initial call
                    user = self.server_recieve_request(client_socket)
                    if self.debug_mode: print(f"{user} added to register of devices.")
                    if user is False: continue #Client disconnected prior to successful connection
                    self.sockets_list.append(client_socket) #Append to select.select list
                    self.network_devices[client_socket] = user #Save client name
                    if self.debug_mode: print('Accepted new connection from {}:{}, station name: {}'.format(*client_addy, user['data'].decode('utf-8')))
                    # print(self.sockets_list)
                else:
                    message = self.server_recieve_request(notified_socket)
                    # if message == "Connection Volatile?": continue
                    if message is False:
                        if self.debug_mode: print('Closed connection from: {}'.format(self.network_devices[notified_socket]['data'].decode('utf-8')))
                        self.sockets_list.remove(notified_socket)
                        del self.network_devices[client_socket]
                        continue
                    user = self.network_devices[notified_socket]
                    if self.debug_mode: print(f"Recieved request from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

                    #TODO: CONVERT TO ONLY SEND TO SELECTED PRINTERS!
                    for client_socket in self.network_devices:
                        if self.debug_mode: print(f"Attempting to submit data to {client_socket}.")
                        if client_socket != notified_socket: #this will not attempt to inform the server lol
                            # client_socket.send(user['header']+user['data']+message['header']+message['data'])
                            client_socket.send(message['header']+message['data'])
                        else: #Let's also let the server do stuff?
                            if self.debug_mode: print(f"Server (Client) processing {message['data'].decode('utf-8')}")
                            self.process_inbound(message['data'].decode('utf-8'))
            for notified_socket in exception_socket:
                print(f"Remvoing exception: {notified_socket}")
                self.sockets_list.remove(notified_socket)
                del self.network_devices[notified_socket]

    def connect_to_server(self):
        if self.debug_mode: print("Activating client -> server module.")
        self.socket.connect((self.server_ip, self.server_port)) #Connect to server
        self.socket.setblocking(False)                        #Set connection to non-blocking state
        printer_name = self.user_position.encode("utf-8")               #On initial contact, format name to server "who" we are
        printer_name_header = f"{len(printer_name):<{self.header_len}}".encode('utf-8')
        if self.debug_mode: print(f"Network printer {printer_name} attempting connection...")
        self.socket.send(printer_name_header + printer_name)                        #Send server who we are
        if self.debug_mode: print(f"Connecting to server...")
        self.network_active = True

    def subscribe(self, device):
        print("Ok so the idea here is that we don't have to print to everyone...")
        #idk how to achieve that lol

    def use_server(self): #https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/?completed=/server-chatroom-sockets-tutorial-python-3/
        self.connect_to_server()
        # self.recieve_strips()                                 #Once in, allow us to recieve strips (prep for GI message integration.)
        try:
            while True:
                printer_name_header = self.socket.recv(self.header_len)
                if self.debug_mode: print(f"Client recieved {printer_name_header}.")
                if not len(printer_name_header): print("Connection closed by server...")
                acid_header = self.socket.recv(self.header_len)
                acid_len = int(acid_header.decode('utf-8').strip())
                acid = self.socket.recv(acid_len).decode('utf-8')
                if self.debug_mode: print(f"Processing {acid}")
                self.process_inbound(acid)
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Network Client Error: {}'.format(str(e)))
            # continue #Didn't recieve anything
        except Exception as e:
            print('Network Client Error: {}'.format(str(e)))

    def process_inbound(self, data):
        if self.debug_mode: print(f"Processing inbound: {data}")
        json_file = self.data_collector.get_json()
        flag = "Print"
        if data.upper()[:2] == "GI": flag = "GI_MSG"
        if flag == "GI_MSG":
            self.printer.print_gi_messages(data)
        elif flag == "Print":
            if self.debug_mode: print(f"We are handling a PRINT job for {data}.")
            #If we recieve a print flight strip instruction, we'll need to convert the CID to the callsign...
            #TODO: Process VISUAL SEPERATION flag. For now, we'll ignore that.
            data = str(data)
            if data[0].isalpha(): data = data[1:] #Remove visual separation flag lol
            for flight in json_file["pilots"]:
                # print(flight)
                # print(flight["cid"])
                # print(f"Does {data} equal to {flight['cid']}? The callsign would be {flight['callsign']}. Survey says {flight['cid'] == data}!")
                if str(flight["cid"]) == data:
                    # self.callsign_requester.request_callsign(flight["callsign"]).
                    callsign_to_print = flight["callsign"]
                    if self.debug_mode: print(f"Callsign located... {self.data_collector.get_callsign_data(callsign_to_print)}, {callsign_to_print}, {self.control_area}")
                    self.printer.print_callsign_data(self.data_collector.get_callsign_data(callsign_to_print), callsign_to_print, self.control_area)
                    break #This may need to be continue(?)

    def server_recieve_request(self, client_socket):
        try:
            # print(f"Recieved request from {client_socket.recv(self.header_len).decode('utf-8')}")
            # print(client_socket.recv(self.header_len).decode('utf-8'))
            message_head = client_socket.recv(self.header_len)#.decode('utf-8')      #gotta add the header info to process how much data to process for GI shit... damn...
            if self.debug_mode: print(f"SERVER recieved MESSAGE HEADER LENGTH {len(message_head)}...")
            if not len(message_head): 
                if self.debug_mode: print("no no no!")
                if self.debug_mode: print("Guess they lost connection?")
                # return "Connection Volatile?"
                return False
            message_len = int(message_head.decode('utf-8').strip())
            if self.debug_mode: print("he shoots")
            return {'header':message_head, 'data':client_socket.recv(message_len)}
        except Exception as e:
            print(f"EXCEPTION in Network / Server_Recieve_Request failed: {e}")
            return False  

    def send_outbound(self, callsign):
        try:
            if callsign:
                print(f"NETWORK MODULE is attempting to send {callsign} to server.")
                callsign = callsign.encode('utf-8')
                if self.debug_mode: print("Callsign encoded.")
                callsign_header = f"{len(callsign):<{8}}".encode('utf-8')
                if self.debug_mode: print("Callsign Header encoded.")
                self.socket.send(callsign_header + callsign)
                if self.debug_mode: print("sent successfullyyyyy")
        except Exception as e:
            print(f"Exception in NETWORK: {e}")
            if callsign:
                self.connect_to_server()
                callsign = callsign.encode('utf-8')
                if self.debug_mode: print("Callsign encoded.")
                callsign_header = f"{len(callsign):<{self.header_len}}".encode('utf-8')
                if self.debug_mode: print("Callsign Header encoded.")
                self.socket.send(callsign_header + callsign)
                print("sent successfullyyyyy")
                self.socket.close()

    # def recieve_strips(self):
    #     while self.network_active:                           #Let us break it off if we want to eventually lol
    #         try:
    #             data = self.socket.recv(self.header_len).decode('utf-8')
    #             print(data)
    #         except:
    #             print(f"Error!")
