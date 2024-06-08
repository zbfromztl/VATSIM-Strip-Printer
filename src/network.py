import socket

#Well, that's all folks!
class Network():
  def __init__(self) -> None:
    #Config network data.
    port = "9511"
    print("Initializing electronic flight strip transfer system configurator...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Determine "where" server is.
    server_ip = ""
    server_ip = input("Please input the IP of the server. Leave blank if this machine is the server: ")
    if server_ip = "":
      server_ip = socket.gethostname()
    print(f"Server IP set to {server_ip}.")
