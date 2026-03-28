import socket, threading, config, sys 

session_active = threading.Event()
session_active.set()

#Thread 1 - le comandos do usuario e envia ao servidor
def negotiator(server_socket):

    while session_active.is_set():
        try:

            cmd = input()  # aguarda o usuário digitar algo
            if not cmd:
                continue

            server_socket.send(cmd.encode()) 

            if cmd.strip().lower() == ':exit':
                print("[OK] Encerrando conexão...")
                session_active.clear()
                break # Para de ler o teclado 

                                        #ouvidor do server
        except(ConnectionResetError,    # except captura erros e exibe
               OSError,
               socket.timeout,          # timeout no socket
               socket.gaierror,         # erro ao resolver DNS/endereço
               socket.herror            # erro de de endereço do host
              ):
            print(f'\n[ERROR] Erro ao se conectar. Conexão Encerrada.')
            session_active.clear()
            break

#thread 2 - recebe os precos do server e printa
def feedupd(server_socket):

    while session_active.is_set():
        try:
            
            msg = server_socket.recv(1024).decode()  # recebe do servidor

            if not msg:
                print('\n[INFO] Servidor encerrou a conexão.')
                session_active.clear()
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
            if session_active.is_set():

                print(f'\n[ERROR] Erro ao se conectar. Conexão Encerrada.')
            
            session_active.clear()
            break


def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #inicia o socket do client    
    
    try:
        server_socket.connect((config.HOST, config.PORT)) # Conecta com o server
    except (ConnectionRefusedError, OSError) as e:
        print(f"[ERROR] Não foi possivel conectar ao servidor: {e}")
        server_socket.close() #libera o socket mesmo sem ter conectado
        sys.exit(1)  #encerra o programa de forma mais limpa

    try:
        clstart = server_socket.recv(1024).decode()
        print(clstart, end="", flush=True) #exibe pedido vindo do server, end="" para facilitar entendimento no terminal, flush=True para otimizar terminal pro user

        username = input()
        server_socket.send(username.encode()) #coleta e envio de username

        msg = server_socket.recv(1024).decode()
        print(f"{msg}\n")

    except (ConnectionResetError, OSError) as e: #Server caiu o login fail
        
        print(f"\n[ERROR] Conexão perdida durante o login: {e}")
        server_socket.close()
        sys.exit(1)

    ClTh1Negotiation = threading.Thread(target = negotiator, args=(server_socket,),name="ClTh1Negotiation")
    ClTh2Feed = threading.Thread(target = feedupd , args=(server_socket,),name="ClTh2Feed") 

    ClTh1Negotiation.start()
    ClTh2Feed.start()

    ClTh1Negotiation.join()  # main() trava aqui até Thread 1 terminar
    
    session_active.clear()
    server_socket.close()

    print(f"\nDesconectado.")

main()



