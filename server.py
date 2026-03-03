import socket, threading, time, random, config
from datetime import datetime

mutex = threading.Lock()

prices = {asset: price for asset, price in config.INITIAL_ASSETS.items()}
balance = config.USER_BALANCE
portfolio = {asset: 0 for asset in config.INITIAL_ASSETS}
tick = config.TICK_SIZE
var_tick = config.MAX_TICKS_PER_VARIATION
min_price = config.MIN_PRICE

#######################
# Thread dos Comandos #
#######################

def commands(client_socket):
    while True:
        #message = client_socket.accept()
        message = client_socket.recv(1024).decode() # corrigido, o "client_socket" não tem .accept


        # Continuar


######################
##  Thread do feed  ##
######################

def market_simulation(client_socket): #ARRUMAR POIS, TICK DE ENVIO = TICK DE ATUALIZAÇÃO, ESTA ERRADO DEPOIS ARRUMO!
    
    while True:
        
        
        feedMsg = "\n" #zera valor de feedmsg para começar atualização de preços
            with mutex:  #para evitar que outra thread não mude os valores 
                for asset, price in prices.items():
                    
                    variation = random.uniform(-tick*var_tick, tick*var_tick) #variação de tick corrigida
                    prices[asset] = round(prices[asset] + variation, 2)  #arredonda preço para 2 casas decimais
           
                    if prices[asset] < min_price: #impede que preço seja menor ou igual a 0
                        prices[asset] = min_price

                    feedMsg += f"{asset}: R${prices[asset]:.2f}\n" #armazena os preços em feedMsg
        
        try:
            client_socket.send(feedMsg.encode()) #manda mensagem pro cliente receber os preços
        except (BrokenPipeError, ConnectionResetError, OSError):
            print("Cliente desconectou. Encerrando o feed.")
            break
        time.sleep(random.uniform(config.MIN_TICK_TIME, config.MAX_TIME_TICK)) # substitui randint por variavel global

###################

def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((config.HOST, config.PORT))
    server_socket.listen(1) #recebe 1 valor na fila, talvez alterar!?

    print(f"[INFO] AGUARDANDO CONEXÃO (PORTA: {config.PORT})")
    client_socket, address = server_socket.accept() # Fica esperando a conexão do cliente p/ aceitar
    print(f"[INFO] CLIENTE CONECTADO: {address}")

    timestamp_message = datetime.now().strftime("%H:%M:%S")
    msg = f"{timestamp_message}: CONNECTED!"

    for asset, price in prices.items():
        msg += f"\nAtivo disponível: {asset} (R${price})\n"
    msg += f"Seu saldo: R${balance}"

    client_socket.send(msg.encode()) # Pra mandar tudo por só um socket

    th1Commands = threading.Thread(target = commands, args=(client_socket,),name="Th1Commands") #Alterei os nomes das threads pra ficar mais claro e adicionei "name" pra cada uma delas
    th2Pricing = threading.Thread(target = market_simulation, args=(client_socket,),name="Th2Pricing")

    th2Pricing.daemon = True #daemon faz com que thread encerre junto com o main
    #th1Commands.daemon = True ------->> Removi Daemon pois commands não precisa dele  //// poderia ser feito com .join(), fazendo com que commands encerre main(), mas teriamos problemas ao expandir para mais clientes
    
    th1Commands.start()      #inicia thread
    th2Pricing.start()

    '''
    Fiz até aqui, daqui pra baixo (nessa funçao), continuar editando
    '''

    msg = client_socket.recv(1024).decode() # Recebe até 1024 bytes de mensagem
    print(f"[INFO] RECEBIDO: {msg}")

    client_socket.close()
    server_socket.close()

main()

