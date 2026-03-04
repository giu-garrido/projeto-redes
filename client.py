import socket, threading, config

















def negotiator(server_socket):

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
            
def feedupd(server_socket):
    while True

    
    try:
            

            
                                        

        except(ConnectionResetError,    # except captura erros e exibe
               OSError,
               socket.timeout,          # timeout no socket
               socket.gaierror,         # erro ao resolver DNS/endereço
               socket.herror            # erro de de endereço do host
              ):
            print(f'/nErro ao se conectar. Conexão Encerrada.')
            break


    
    

def main():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #inicia o socket do client    
    client_socket.connect((config.HOST, config.PORT)) # Conecta com o server

    msg = client_socket.recv(1024).decode() # Recebe até 1024 bytes de mensagem
    print(f"Server says: {msg}")
    
    server_socket, address = client_socket.accept()



'''
Parte das Threads
'''
    ClTh1Negotiation = threading.Thread(target = negotiator, args=(server_socket,),name="ClTh1Negotiation")
    ClTh2Feed = threading.Thread(target = feedupd , args=(server_socket,),name="ClTh2Feed") 

    ClTh1Negotiation.daemon = True
    #ClTh2Feed.daemon = True ----- comentei pq n sei se é válido usar aqui

    ClTh1Negotiation.start()
    ClTh2Feed.start()

    
    #client_socket.send("Testando (client side)".encode()) ----- teste antigo
    
    client_socket.close()
    server_socket.close()
'''
Parte das Threads
'''

main()



