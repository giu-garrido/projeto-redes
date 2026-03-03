import socket, threading, time, random, config
from datetime import datetime

mutex = threading.Lock()

with mutex:
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

def market_simulation(client_socket):
    
    while True:
        for asset, price in prices.items():
            variation = random.uniform(-tick, tick*var_tick)
            prices[asset] = round(prices[asset] + variation, 2)
           

            if prices[asset] < min_price:
                prices[asset] = min_price

            feed_msg += f"{asset}: R${price:.2f}\n" #adicionei o que faltava nessa função, ela atualizava os preços e conferia com o minimo, mas não enviava nada para o client
            client_socket.send(feed_msg.encode())
            time.sleep(config.FEED_INTERVAL)

            # Continuar

        time.sleep(config.FEED_INTERVAL) # substitui random por variavel global

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

    th1Commands = threading.Thread(target = commands, args=(client_socket,),name="ThCommands") #Alterei os nomes das threads pra ficar mais claro e adicionei "name" pra cada uma delas
    th2Pricing = threading.Thread(target = market_simulation, args=(client_socket,),name="ThPricing")

    thMarketPricing.daemon = True #daemon faz com que thread encerre junto com o main
    #thCommands.daemon = True ------->> Removi Daemon pois commands não precisa dele  //// poderia ser feito com .join(), fazendo com que commands encerre main(), mas teriamos problemas ao expandir para mais clientes
    
    thCommands.start()      #inicia thread
    thPricing.start()

    '''
    Fiz até aqui, daqui pra baixo (nessa funçao), continuar editando
    '''

    msg = client_socket.recv(1024).decode() # Recebe até 1024 bytes de mensagem
    print(f"[INFO] RECEBIDO: {msg}")

    client_socket.close()
    server_socket.close()

main()

