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
        message = client_socket.accept()

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

            # Continuar

        time.sleep(random.randint(1,3))

###################

def main():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((config.HOST, config.PORT))
    server_socket.listen(1)

    print(f"[INFO] AGUARDANDO CONEXÃO (PORTA: {config.PORT})")
    client_socket, address = server_socket.accept() # Fica esperando a conexão do cliente p/ aceitar
    print(f"[INFO] CLIENTE CONECTADO: {address}")

    timestamp_message = datetime.now().strftime("%H:%M:%S")
    msg = f"{timestamp_message}: CONNECTED!"

    for asset, price in prices.items():
        msg += f"\nAtivo disponível: {asset} (R${price})\n"
    msg += f"Seu saldo: R${balance}"

    client_socket.send(msg.encode()) # Pra mandar tudo por só um socket

    t1 = threading.Thread(target = commands, args=(client_socket,))
    t2 = threading.Thread(target = market_simulation, args=(client_socket,))

    t1.start()
    t2.start()

    '''
    Fiz até aqui, daqui pra baixo (nessa funçao), continuar editando
    '''

    msg = client_socket.recv(1024).decode() # Recebe até 1024 bytes de mensagem
    print(f"[INFO] RECEBIDO: {msg}")

    client_socket.close()
    server_socket.close()

main()

