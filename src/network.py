import socket

#Well, that's all folks!
class Network():
  def __init__(self) -> None:
    #Config network data.
    Privacy_mode = False
    self.is_server_host = False
    self.server_port = 9511
    print("Initializing electronic flight strip transfer system configurator...")
    self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Determine "where" server is.
    self.server_ip = ""
    self.server_ip = input("Please input the IP of the server. Leave blank if this machine is the server: ")
    self.server_ip = self.server_ip.strip()
    if self.server_ip == "":
      self.server_ip = socket.gethostname()
      self.is_server_host = True
    if Privacy_mode == False: #Privacy Mode is only togglable in this file. If its DISABLED, it should show the user their IP and PORT so that other machines can connect.
      print(f"Server IP set to {self.server_ip}. Port number {self.server_port}.")
    self.network_devices = dict() #This is a list of all available "devices" on our server. Really, it should just list each position thats connected.
    self.target_machines = set()  #This is a list of printers that we want our strips to go out to.
    
    #TODO: Add logic to connect to server if it isn't "this" machine.
    #TODO: Add logic to process printer connecting/unresponsive(disconnect) to server.
    #TODO: Process "send strip to departure" message.

  def run_server(self):
    #try:  #This logic is flawed (it throws an error and then continues to attempt the server lol)
    self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.server_socket.bind(self.server_ip, self.server_port)
    self.server_socket.listen()
    # except:
    #   print("Unable to initialize server.")

    while True:
      clientsocket, address = self.server_socket.accept()
      
