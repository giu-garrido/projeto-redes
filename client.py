import socket, threading, config

active = config.ACTIVE

#Thread 1 - le comandos do usuario e envia ao servidor
def negotiator(server_socket):
    global active

    while active:
        try:
            #Commit Victor
            cmd = input()  # aguarda o usuário digitar algo
            if not cmd:
                continue

            server_socket.send(cmd.encode()) 

            if cmd.strip().lower() == ':exit':
                print("Encerrando conexão...")
                active = False
                break # Para de ler o teclado

            else:
                print(server_socket.recv(1024).decode())     

                                        #ouvidor do server
        except(ConnectionResetError,    # except captura erros e exibe
               OSError,
               socket.timeout,          # timeout no socket
               socket.gaierror,         # erro ao resolver DNS/endereço
               socket.herror            # erro de de endereço do host
              ):
            print(f'/n[ERROR] Erro ao se conectar. Conexão Encerrada.')
            active = False
            break

#thread 2 - recebe os precos do server e printa
def feedupd(server_socket):
    global active

    while active:
        try:
            #commit victor
            msg = server_socket.recv(1024).decode()  # recebe do servidor
            if not msg:
                print('\nServidor encerrou a conexão.')
                active = False
                break
            print(msg)  # exibe os precos
            #/commit victor
        
        except(ConnectionResetError,    # except captura erros e exibe
                OSError,
                socket.timeout,          # timeout no socket
                socket.gaierror,         # erro ao resolver DNS/endereço
                socket.herror            # erro de de endereço do host
                ):
            print(f'/n[ERROR] Erro ao se conectar. Conexão Encerrada.')
            active = False
            break


def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #inicia o socket do client    
    server_socket.connect((config.HOST, config.PORT)) # Conecta com o server

    msg = server_socket.recv(1024).decode() # Recebe até 1024 bytes de mensagem
    print(f"Server says: {msg}")


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
    
    server_socket.close()

main()



