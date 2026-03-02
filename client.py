import socket, threading, config

def main():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((config.HOST, config.PORT)) # Conecta com o server

    msg = client_socket.recv(1024).decode() # Recebe até 1024 bytes de mensagem
    print(f"Server says: {msg}")

    client_socket.send("Testando (client side)".encode())

    client_socket.close()

main()