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
                print("[OK] Encerrando conexão...")
                active = False
                break # Para de ler o teclado 

                                        #ouvidor do server
        except(ConnectionResetError,    # except captura erros e exibe
               OSError,
               socket.timeout,          # timeout no socket
               socket.gaierror,         # erro ao resolver DNS/endereço
               socket.herror            # erro de de endereço do host
              ):
            print(f'\n[ERROR] Erro ao se conectar. Conexão Encerrada.')
            active = False
            break

#thread 2 - recebe os precos do server e printa
def feedupd(server_socket):
    global active

    while active:
        try:
            
            msg = server_socket.recv(1024).decode()  # recebe do servidor

            if not msg:
                print('\n[INFO] Servidor encerrou a conexão.')
                active = False
                break

            if "[ERROR]" in msg:
                print(f"\033[31m{msg}\033[0m") # Texto sai em vermelho se for erro
            else:
                print(msg)
          
        
        except(ConnectionResetError,    # except captura erros e exibe
                OSError,
                socket.timeout,          # timeout no socket
                socket.gaierror,         # erro ao resolver DNS/endereço
                socket.herror            # erro de de endereço do host
                ):
            print(f'\n[ERROR] Erro ao se conectar. Conexão Encerrada.')
            active = False
            break


def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #inicia o socket do client    
    server_socket.connect((config.HOST, config.PORT)) # Conecta com o server

    msg = server_socket.recv(1024).decode()
    print(f"{msg}\n")

    ClTh1Negotiation = threading.Thread(target = negotiator, args=(server_socket,),name="ClTh1Negotiation")
    ClTh2Feed = threading.Thread(target = feedupd , args=(server_socket,),name="ClTh2Feed") 

    ClTh1Negotiation.start()
    ClTh2Feed.start()

    ClTh1Negotiation.join()  # main() trava aqui até Thread 1 terminar
    
    server_socket.close()

main()



