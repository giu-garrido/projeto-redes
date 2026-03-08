import socket, threading, config

#Thread 1 - le comandos do usuario e envia ao servidor
def negotiator(server_socket):

    while True:
        try:
            #Commit Victor
            cmd = input()  # aguarda o usuário digitar algo
            if not cmd:
                continue

            client_socket.send(cmd.encode())  # envia pro servidor

            if cmd.strip().lower() == ':exit': #user pode digitar exit para finalizar o programa
                print("Encerrando conexão...")
                break                   
            #/commit victor
                                        #ouvidor do server
        except(ConnectionResetError,    # except captura erros e exibe
               OSError,
               socket.timeout,          # timeout no socket
               socket.gaierror,         # erro ao resolver DNS/endereço
               socket.herror            # erro de de endereço do host
              ):
            print(f'/nErro ao se conectar. Conexão Encerrada.')
            break

#thread 2 - recebe os precos do server e printa
def feedupd(server_socket):
    while True:
    try:
        #commit victor
        msg = client_socket.recv(1024).decode()  # recebe do servidor
            if not msg:
                print('\nServidor encerrou a conexão.')
                break
            print(msg)  # exibe os precos
        #/commit victor
    
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

    # commit victor 
    #server_socket, address = client_socket.accept()
    # --- pelo que entendi, o .accept só existe no server, o client só se conecta pelo .connect e ja usa o socket tbm
    #/commit victor

'''
Parte das Threads
'''
    ClTh1Negotiation = threading.Thread(target = negotiator, args=(server_socket,),name="ClTh1Negotiation")
    ClTh2Feed = threading.Thread(target = feedupd , args=(server_socket,),name="ClTh2Feed") 

    #commit victor
    #ClTh1Negotiation.daemon = True 
    #----- n pode usar daemon aqui, pq como ela le a digitaçao do user, ela pode acabar "morrendo" sem o usuario perceber no meio da digitaçao
    #/commit victor

    #ClTh2Feed.daemon = True ----- comentei pq n sei se é válido usar aqui #victor: realmente, nao é valido!

    ClTh1Negotiation.start()
    ClTh2Feed.start()

    #victor 
    ClTh1Negotiation.join()  # main() trava aqui até Thread 1 terminar
    #/victor

    #client_socket.send("Testando (client side)".encode()) ----- teste antigo
    
    client_socket.close()

    #server_socket.close() #victor: como removi o .accept anteriormente essa variavel nunca existiu (e nem precisa)
'''
Parte das Threads
'''

main()



