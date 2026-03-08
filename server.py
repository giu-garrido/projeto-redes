import socket, threading, time, random, config
from datetime import datetime

mutex = threading.Lock()

prices = {asset: price for asset, price in config.INITIAL_ASSETS.items()}
balance = config.USER_BALANCE
portfolio = {asset: 0 for asset in config.INITIAL_ASSETS}
tick = config.TICK_SIZE
var_tick = config.MAX_TICKS_PER_VARIATION
min_price = config.MIN_PRICE
feed_interval = config.FEED_INTERVAL
active = config.ACTIVE
min_tick_time = config.MIN_TICK_TIME
max_tick_time = config.MAX_TICK_TIME

#######################
# Thread dos Comandos #
#######################

def commands(client_socket):
    global balance, active

    while True:

        message = client_socket.recv(1024).decode()

        if not message:
            break

        message = message.strip()

        if message.lower() == ":exit":
            client_socket.send("[INFO] Desconectando...".encode())
            active = False
            break # Para de processar comandos


        elif message.lower() == ":carteira":
            with mutex:
                text = "\n---------CARTEIRA---------\n"
                text += f"Saldo: R${balance:.2f}\n"

                for asset, qtd in portfolio.items():
                    if qtd > 0:
                        total_value = qtd * prices[asset]

                        text += f"[{asset}]: {qtd} unidades (Total: R${total_value:.2f})\n"

                text += "\n---------------------------\n"
            client_socket.send(text.encode())


        elif message.lower().startswith(":buy"):
            parts = message.split()

            if len(parts) == 3: # Pra só aceitar o comando na estrutura correta
                asset = parts[1].upper()

                try:
                    qtd = int(parts[2])

                except ValueError:
                    client_socket.send("[ERROR] Quantidade deve ser um número inteiro.".encode())
                    continue

                with mutex:
                    if asset in prices:
                        current_price = prices[asset]
                        total_cost = current_price * qtd

                        if balance >= total_cost:
                            balance -= total_cost
                            portfolio[asset] += qtd
                            response = f"\n[OK] Você comprou: {qtd}x {asset} a R${current_price:.2f} | Total: R${total_cost:.2f}"
                        
                        else:
                            response = f"\n[ERROR] Saldo insuficiente. Saldo atual: R${balance:.2f}"
                    else:
                        response = f"\n[ERROR] Ativo '{asset}' não encontrado."

                client_socket.send(response.encode())
            else:
                client_socket.send("\n[ERROR] Comando correto: :buy <ATIVO> <QTD>".encode())


        elif message.lower().startswith(":sell"):
            parts = message.split()

            if len(parts) == 3: # Pra só aceitar o comando na estrutura correta
                asset = parts[1].upper()

                try:
                    qtd = int(parts[2])
                except ValueError:
                    client_socket.send("[ERROR] Quantidade deve ser um número inteiro.".encode())
                    continue

                with mutex:
                    if asset in prices:
                        current_price = prices[asset]
                        total_cost = current_price * qtd

                        if asset in portfolio and portfolio[asset] >= qtd:
                            balance += total_cost
                            portfolio[asset] -= qtd
                            response = f"\n[OK] Você vendeu: {qtd}x {asset} a R${current_price:.2f} | Total: R${total_cost:.2f}"
                        
                        else:
                            response = f"\n[ERROR] Você não possui {qtd}x {asset}. Disponível: {portfolio.get(asset, 0)} unidades."
                    else:
                        response = f"\n[ERROR] Ativo '{asset}' não encontrado."

                client_socket.send(response.encode())
            else:
                client_socket.send("\n[ERROR] Comando correto: :sell <ATIVO> <QTD>".encode())
                

        else:
            client_socket.send("\n[ERROR] Comando não reconhecido. Use :buy, :sell, :carteira, :exit".encode())



######################
##  Thread do feed  ##
######################

def market_simulation(client_socket):  
    global active, feed_interval, prices, min_price, var_tick, tick, min_tick_time, max_tick_time

    cont = 0                          
    tempo = 0

    while True:
        time.sleep(feed_interval - tempo) #no pior dos casos, seria (5 - 1) ou (5-3)
        cont += 1        
        feedMsg = "\n" #zera valor de feedmsg para começar atualização de preços

        with mutex:  #para evitar que outra thread não mude os valores 
            for asset, price in prices.items():
                    
                variation = random.uniform(-tick*var_tick, tick*var_tick) 
                prices[asset] = round(prices[asset] + variation, 2)  
           
                if prices[asset] < min_price: #impede que preço seja menor ou igual a 0
                    prices[asset] = min_price

                    feedMsg += f"{asset}: R${prices[asset]:.2f}\n" #armazena os preços em feedMsg

        if(cont != 1):
            tempo = random.uniform(min_tick_time, max_tick_time)
            time.sleep(tempo)

        else:
            tempo = 0

        try:
            client_socket.send(feedMsg.encode()) #manda mensagem pro cliente receber os preços

        except (BrokenPipeError, ConnectionResetError, OSError):
            print("[INFO] Cliente desconectou. Encerrando o feed.")
            break

        time.sleep(tempo) # substitui randint por variavel global
        
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

    SvTh1Commands = threading.Thread(target = commands, args=(client_socket,),name="SvTh1Commands") #Alterei os nomes das threads pra ficar mais claro e adicionei "name" pra cada uma delas
    SvTh2Pricing = threading.Thread(target = market_simulation, args=(client_socket,),name="SvTh2Pricing")

    SvTh2Pricing.daemon = True #daemon faz com que thread encerre junto com o main
    #th1Commands.daemon = True ------->> Removi Daemon pois commands não precisa dele  //// poderia ser feito com .join(), fazendo com que commands encerre main(), mas teriamos problemas ao expandir para mais clientes
    
    SvTh1Commands.start()      #inicia thread
    SvTh2Pricing.start()

    '''
    Fiz até aqui, daqui pra baixo (nessa funçao), continuar editando
    '''

    msg = client_socket.recv(1024).decode() # Recebe até 1024 bytes de mensagem
    print(f"[INFO] RECEBIDO: {msg}")

    client_socket.close()
    server_socket.close()

main()

