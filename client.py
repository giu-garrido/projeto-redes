import socket, threading, config

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((config.HOST, config.PORT)) # Conecta com o server

msg = server.recv(1024).decode() # Recebe até 1024 bytes de mensagem
print(f"Server says: {msg}")

server.send("Testing (client side)".encode())

server.close()