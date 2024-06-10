import socket
from Printer import Printer

#Well, that's all folks!
class Network():
    def __init__(self) -> None:
        self.debug_mode = True #For dev work... lol
        #Config network data.
        Privacy_mode = False
        self.is_server_host = False
        self.network_active = False
        self.server_port = 9511
        print("Initializing electronic flight strip transfer system configurator...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Determine "where" server is.
        self.server_ip = ""
        self.server_ip = input("Please input the IP of the server. Leave blank if this machine is the server: ")
        self.server_ip = self.server_ip.strip()
        if self.server_ip == "":
            self.server_ip = socket.gethostbyname(socket.gethostname())
            self.is_server_host = True
        if Privacy_mode == False: #Privacy Mode is only togglable in this file. If its DISABLED, it should show the user their IP and PORT so that other machines can connect.
            print(f"Server IP set to {self.server_ip}. Port number {self.server_port}.")
        self.header_len = 7
        if self.debug_mode: print(f"Header length is set to {self.header_len}.")
        self.network_devices = dict() #This is a list of all available "devices" on our server. Really, it should just list each position thats connected.
        self.target_machines = set()  #This is a list of printers that we want our strips to go out to.
        
        if self.is_server_host:
            self.run_server()
        #TODO: Add logic to connect to server if it isn't "this" machine.
        #TODO: Add logic to process printer connecting/unresponsive(disconnect) to server.
        #TODO: Process "send strip to departure" message.
        #TODO EVENTUALLY: Store times on here lol.

    def run_server(self): #https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
        #try:  #This logic is flawed (it throws an error and then continues to attempt the server lol)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_ip, self.server_port)
        self.socket.listen()
        if self.debug_mode: print(f"Server running.")
        # except:
        #   print("Unable to initialize server.")

        while True:
            clientsocket, address = self.socket.accept()
            if self.debug_mode: print(f"Client {clientsocket} connected.")

    def join_server(self, position): #https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/?completed=/server-chatroom-sockets-tutorial-python-3/
        self.socket.connect(self.server_ip, self.server_port) #Connect to server
        self.socket.setblocking(False)                        #Set connection to non-blocking state
        printer_name = position.encode("utf-8")               #On initial contact, format name to server "who" we are
        self.socket.send(printer_name)                        #Send server who we are
        self.network_active = True
        self.recieve_strips()                                 #Once in, allow us to recieve strips (prep for GI message integration.)
        
    def relay_strips(self, client_sock):
        print(":)")

    def server_recieve_request(self):
        try:
            message = self.socket.recv(self.header_len)      #gotta add the header info to process how much data to process for GI shit... damn...
        
        except:
            return False  

    def recieve_strips(self):
        while self.network_active:                           #Let us break it off if we want to eventually lol
            try:
                data = self.socket.recv(self.header_len).decode('utf-8')
                print(data)
            except:
                print(f"Error!")