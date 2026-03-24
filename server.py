import socket, threading, time, random, config, sys, os, json
from datetime import datetime

mutex = threading.Lock()
mutex_clients = threading.Lock()

prices = {asset: price for asset, price in config.INITIAL_ASSETS.items()}
users = {}
active_usernames = set()

max_clients = 0
clients_connected = 0
server_running = threading.Event()
server_running.set()

tick = config.TICK_SIZE
var_tick = config.MAX_TICKS_PER_VARIATION
min_price = config.MIN_PRICE
feed_interval = config.FEED_INTERVAL
min_tick_time = config.MIN_TICK_TIME
max_tick_time = config.MAX_TICK_TIME

#############################
# Criação dos Arquivos JSON #
#############################

def load_users():
    
    global users

    if os.path.exists(config.DATA_FILE):
        
        try:
            
            with open(config.DATA_FILE, "r") as f:
                users = json.load(f)
            print(f"[INFO] Dados carregados de {config.DATA_FILE} (temos {len(users)} usuário(s))")
        
        except (json.JSONDecodeError, IOError) as e:
            print(f"[ERROR] Falha ao carregar {config.DATA_FILE}: {e}")
            users = {}
    else:
        print(f"[INFO] Arquivo {config.DATA_FILE} não encontrado. Iniciando sem dados.")
        users = {}
 
 
def save_users():
   
    try:
        
        with open(config.DATA_FILE, "w") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    except IOError as e:
        print(f"[ERROR] Falha ao salvar {config.DATA_FILE}: {e}")

#######################
# Thread dos Comandos #
#######################

def commands(client_socket, username, session_active):

    while session_active.is_set():

        try:

            message = client_socket.recv(1024).decode()

        except (ConnectionResetError, OSError):
            print(f"[INFO] {username} desconectou.")

        if not message:
            print(f"[INFO] {username} encerrou a conexão.")
            break

        message = message.strip()

        if message.lower() == ":exit":
            client_socket.send("[INFO] Desconectando...".encode())
            break # Para de processar comandos


        elif message.lower() == ":carteira":
            with mutex:
                text = "\n---------CARTEIRA---------\n"
                text += f"Saldo: R${users[username]['balance']:.2f}\n"

                for asset, qtd in users[username]['portfolio'].items():
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

                        if users[username]['balance'] >= total_cost:
                            users[username]['balance'] -= total_cost
                            users[username]['portfolio'][asset] += qtd
                            response = f"\n[OK] Você executou: COMPRA {qtd}x {asset} a R${current_price:.2f} | Total: R${total_cost:.2f}"
                            save_users()

                        else:
                            response = f"\n[ERROR] Saldo insuficiente. Saldo atual: R${users[username]['balance']:.2f}"
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

                        if asset in users[username]['portfolio'] and users[username]['portfolio'][asset] >= qtd:
                            users[username]['balance'] += total_cost
                            users[username]['portfolio'][asset] -= qtd
                            response = f"\n[OK] Você executou: VENDA {qtd}x {asset} a R${current_price:.2f} | Total: R${total_cost:.2f}"
                            save_users()

                        else:
                            response = f"\n[ERROR] Você não possui {qtd}x {asset}. Disponível: {users[username]['portfolio'].get(asset, 0)} unidades."
                    else:
                        response = f"\n[ERROR] Ativo '{asset}' não encontrado."

                client_socket.send(response.encode())
            else:
                client_socket.send("\n[ERROR] Comando correto: :sell <ATIVO> <QTD>".encode())
                

        else:
            client_socket.send("\n[ERROR] Comando não reconhecido. Use :buy, :sell, :carteira, :exit".encode())

    session_active.clear()

##########################################
##  Thread do feed (agora por cliente)  ##
##########################################

def feed_sender(client_socket, username, session_active):
 
    while session_active.is_set():

        time.sleep(feed_interval)
 
        if not session_active.is_set():
            break
 
        with mutex:
            feed_msg = "\n[FEED] Cotações atualizadas:\n"
            for asset, price in prices.items():
                feed_msg += f"\t{asset}: R${price:.2f}\n"
 
        try:
            client_socket.send(feed_msg.encode())

        except (BrokenPipeError, ConnectionResetError, OSError):
            print(f"[INFO] Feed: {username} desconectou.")
            session_active.clear()
            break


################################
# Simulador de Mercado (único) #
################################


def market_simulation():
 
    while server_running.is_set():

        with mutex:

            for asset in prices:

                variation = random.uniform(-tick * var_tick, tick * var_tick)
                prices[asset] = round(prices[asset] + variation, 2)
 
                if prices[asset] < min_price:
                    prices[asset] = min_price
 
        time.sleep(random.uniform(min_tick_time, max_tick_time))


#########################
##  Thread do waiter   ##
#########################


def client_waiter(client_socket, address):

    global clients_connected

    client_socket.send(f"Digite seu nome de usuário: ".encode()) #pede nome de user
    
    try:
        username = client_socket.recv(1024).decode().strip() 
    except (ConnectionResetError, OSError):
        with mutex_clients:
            clients_connected -= 1
        client_socket.close()
        return


    if not username: #confirma se há nome
        client_socket.send("[ERROR] Nome inválido. Encerrando conexão.".encode())
        with mutex_clients:
            clients_connected -= 1
        client_socket.close()
        return

    with mutex_clients: #confirma se nome ja esta em uso
        if username in active_usernames:
            client_socket.send("[ERROR] Nome de usuário já está em uso. Encerrando conexão.".encode())
            clients_connected -= 1
            client_socket.close()
            return
        active_usernames.add(username)

    with mutex:
        if username not in users:
            users[username] = {
                "balance": config.USER_BALANCE,
                "portfolio": {asset: 0 for asset in config.INITIAL_ASSETS}       
            }
            save_users()
            is_new = True

        else:
        
            for asset in config.INITIAL_ASSETS:
                if asset not in users[username]['portfolio']:
                    users[username]['portfolio'][asset] = 0
            is_new = False


    print(f"[INFO] Usuário identificado: {username} | Endereço: {address}")

    timestamp_message = datetime.now().strftime("%H:%M:%S")

    msg = f"{timestamp_message}: CONECTADO! Bem vindo, {username}!\n"
    msg += "-------------------------------------------\nComandos: :buy <ATIVO> <QTD> | :sell <ATIVO> <QTD> | :carteira | :exit\n-------------------------------------------\n"
    
    with mutex:

        for asset, price in prices.items():
            msg += f"\nAtivo disponível: {asset} (R${price:.2f})\n"
        msg += f"\nSeu saldo: R$ {users[username]['balance']:.2f}"
    
    client_socket.send(msg.encode())

    session_active = threading.Event()
    session_active.set()

    SvTh1Commands = threading.Thread(
        target = commands, 
        args=(client_socket,username, session_active),
        name=f"SvTh1Commands-{address}")
    
    SvTh2Pricing = threading.Thread(
        target = market_simulation, 
        args=(),
        name=f"SvTh2Pricing-{address}")

    SvTh2Pricing.daemon = True #daemon faz com que thread encerre junto com o main
    
    SvTh1Commands.start()
    SvTh2Pricing.start()

    SvTh1Commands.join() # main vai travar até a thread de comandos fechar

    session_active.clear()

    with mutex_clients:
        clients_connected -= 1
        active_usernames.discard(username)

    client_socket.close()
    print(f"[INFO] Cliente {address} desconectou. Clientes: {clients_connected}/{max_clients}")
 

        
###################

def main():
    global max_clients, clients_connected

    
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

    load_users()
    
    print(f"[INFO] Servidor iniciado. Limite: {max_clients} cliente(s).")
    

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #evita endereço já em uso
    server_socket.bind((config.HOST, config.PORT))
    server_socket.listen()

    print(f"[INFO] AGUARDANDO CONEXÃO (PORTA: {config.PORT})")

    th_market = threading.Thread(target=market_simulation, name="MarketSimulation", daemon=True) #cria só uma thread pro market
    
    th_market.start()


    try:
        
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

    except KeyboardInterrupt:
        print(f"\n[INFO] Crtl+C encerrou o servidor.")

    with mutex:
            save_users()
    print("[INFO] Dados salvos. Servidor encerrado.")

    server_socket.close()

main()

