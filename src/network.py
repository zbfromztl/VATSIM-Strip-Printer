import socket

#Well, that's all folks!
class Network():
  def __init__(self) -> None:
    #Config network data.
    Privacy_mode = False
    server_port = "9511"
    print("Initializing electronic flight strip transfer system configurator...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Determine "where" server is.
    server_ip = ""
    server_ip = input("Please input the IP of the server. Leave blank if this machine is the server: ")
    if server_ip == "":
      server_ip = socket.gethostname()
    if Privacy_mode == False:
      print(f"Server IP set to {server_ip}.")
    network_devices = dict()
    
    #TODO: Add logic to connect to server if it isn't "this" machine.
    #TODO: Add logic to process printer connecting/unresponsive(disconnect) to server.
    #TODO: Process "send strip to departure" message. 

  def run_server(self):
    server_socket = self.server_socket
    try:  #This logic is flawed (it throws an error and then continues to attempt the server lol)
      server_socket.bind(int(self.server_ip), int(self.server_port))
      server_socket.listen(6)
    except:
      print("Unable to initialize server.")
    while True:
      clientsocket, address = server_socket.accept()
      
