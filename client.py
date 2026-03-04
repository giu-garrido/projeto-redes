import socket, threading, config

def main():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((config.HOST, config.PORT)) # Conecta com o server

    msg = client_socket.recv(1024).decode() # Recebe até 1024 bytes de mensagem
    print(f"Server says: {msg}")


    ClTh1Negotiation = threading.Thread(target = trocar, args=(trocar,),name="ClTh1Negotiation")
    ClTh2Feed = threading.Thread(target = trocar , args=(trocar,),name="ClTh2Feed") 

    
    client_socket.send("Testando (client side)".encode())
    
    client_socket.close()

main()



def thServerListener(server_socket):

    while True:
        try:
            

            
                                        #ouvidor do server

        except(ConnectionResetError,    # except captura erros e exibe
               OSError,
               socket.timeout,          # timeout no socket
               socket.gaierror,         # erro ao resolver DNS/endereço
               socket.herror            # erro de de endereço do host
              ):
            print(f'/nErro ao se conectar. Conexão Encerrada.')
            break
            



    
    
