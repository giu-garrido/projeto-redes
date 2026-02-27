import socket, threading, time, random, config

mutex = threading.Lock()

prices = {asset: price for asset, price in config.INITIAL_ASSETS.items()}
balance = config.USER_BALANCE
portfolio = {asset: 0 for asset in config.INITIAL_ASSETS}

# Testando conexão

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((config.HOST, config.PORT))
server.listen(1)

print(f"[INFO] AGUARDANDO CONEXÃO (PORTA: {config.PORT})")
client_socket, address = server.accept() # Fica esperando a conexão do cliente p/ aceitar
print(f"[INFO] Client connected: {address}")

client_socket.send("CONNECTED!".encode())
msg = client_socket.recv(1024).decode() # Recebe até 1024 bytes de mensagem
print(f"[INFO] Received: {msg}")

client_socket.close()
server.close()

