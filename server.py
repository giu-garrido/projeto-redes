import socket, threading, time, random, config, sys
from datetime import datetime

mutex = threading.Lock()
mutex_clients = threading.Lock()

prices = {asset: price for asset, price in config.INITIAL_ASSETS.items()}
balance = config.USER_BALANCE
portfolio = {asset: 0 for asset in config.INITIAL_ASSETS}

max_clients = 0
clients_connected = 0

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

    while active:

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
                            response = f"\n[OK] Você executou: COMPRA {qtd}x {asset} a R${current_price:.2f} | Total: R${total_cost:.2f}"
                        
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
                            response = f"\n[OK] Você executou: VENDA {qtd}x {asset} a R${current_price:.2f} | Total: R${total_cost:.2f}"
                        
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
    global active, prices

    beginning_feed_time = time.time()

    while active:
        with mutex:

            for asset, price in prices.items():
                    
                variation = random.uniform(-tick * var_tick, tick * var_tick)
                prices[asset] = round(prices[asset] + variation, 2)

                if prices[asset] < min_price:
                    prices[asset] = min_price

        if (time.time() - beginning_feed_time) >= feed_interval:
            with mutex:
                feed_msg = "\n[FEED] Cotações atualizadas:\n"
                for asset, price in prices.items():
                    feed_msg += f"\t{asset}: R${price:.2f}\n"

            try:
                client_socket.send(feed_msg.encode())
            except (BrokenPipeError, ConnectionResetError, OSError):
                print("[INFO] Cliente desconectou. Encerrando o feed.")
                break

            beginning_feed_time = time.time()

        time.sleep(random.uniform(min_tick_time, max_tick_time))

def client_waiter(client_socket, address):
    global clients_connected

    timestamp_message = datetime.now().strftime("%H:%M:%S")
    msg = f"{timestamp_message}: CONECTADO!"

    msg += "-------------------------------------------\nComandos: :buy <ATIVO> <QTD> | :sell <ATIVO> <QTD> | :carteira | :exit\n-------------------------------------------\n"

    for asset, price in prices.items():
        msg += f"\nAtivo disponível: {asset} (R${price})\n"
    msg += f"Seu saldo: R${balance}"

    client_socket.send(msg.encode()) # Pra mandar tudo por só um socket

    SvTh1Commands = threading.Thread(
        target = commands, 
        args=(client_socket,),
        name=f"SvTh1Commands-{address}")
    
    SvTh2Pricing = threading.Thread(
        target = market_simulation, 
        args=(client_socket,),
        name=f"SvTh2Pricing-{address}")

    SvTh2Pricing.daemon = True #daemon faz com que thread encerre junto com o main
    
    SvTh1Commands.start()
    SvTh2Pricing.start()

    SvTh1Commands.join() # main vai travar até a thread de comandos fechar

    with mutex_clients:
        clients_connected -= 1

    client_socket.close()
    print(f"[INFO] Cliente {address} desconectou. Clientes: {clients_connected}/{max_clients}")
 

        
###################

def main():
    global max_clients

    
    if len(sys.argv) != 2: #verifica se houve o argumento de max_clients
        print("[ERROR] Uso correto: python server.py <max_clients>")
        sys.exit(1) #encerra com codigo de erro
    try:
        max_clients = int(sys.argv[1]) #o argumento em sys é string por padrão
        if(max_clients < 1):
            raise ValueError
    except ValueError:
        print("[ERROR] <max_clientes> deve ser um número inteiro positivo.")
        sys.exit(1)
    print(f"[INFO] Servidor iniciado. Limite: {max_clients} cliente(s).")
    

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((config.HOST, config.PORT))
    server_socket.listen()

    print(f"[INFO] AGUARDANDO CONEXÃO (PORTA: {config.PORT})")

    while True:
        
        client_socket, address = server_socket.accept() # Fica esperando a conexão do cliente p/ aceitar

        with mutex_clients:
            if clients_connected >= max_clients:
                client_socket.send("[ERROR] Servidor lotado. Tente mais tarde.".encode())
                client_socket.close()
                continue
            clients_connected += 1
        print(f"[INFO] CLIENTE CONECTADO: {address} | CLIENTES: {clients_connected}/{max_clients}")

        client_thread = threading.Thread(
            target = client_waiter,
            args = (client_socket, address),
            name = f"Client - {address}"

            
        )
        client_thread.daemon = True
        client_thread.start()


main()

