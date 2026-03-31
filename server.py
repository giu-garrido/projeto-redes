import socket, threading, time, random, config, sys, os, json
from datetime import datetime

mutex = threading.Lock()
mutex_clients = threading.Lock()

prices = {asset: price for asset, price in config.INITIAL_ASSETS.items()}
pending_orders = {}
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
    global users, prices

    if os.path.exists(config.DATA_FILE):
        try:
            with open(config.DATA_FILE, "r") as f:
                data = json.load(f)

            # Carrega preços salvos, se existirem
            if "prices" in data:
                prices.update(data["prices"])
                print(f"[INFO] Preços carregados do disco.")
            else:
                print(f"[INFO] Nenhum preço salvo encontrado. Usando valores iniciais do config.")

            # Carrega usuários — ignora a chave "prices"
            users = {k: v for k, v in data.items() if k != "prices"}
            print(f"[INFO] Dados carregados de {config.DATA_FILE} ({len(users)} usuário(s))")

        except (json.JSONDecodeError, IOError) as e:
            print(f"[ERROR] Falha ao carregar {config.DATA_FILE}: {e}")
            users = {}
    else:
        print(f"[INFO] Arquivo {config.DATA_FILE} não encontrado. Usando valores iniciais.")
        users = {}
 
 
def save_users():
   
    try:
        data = {"prices": prices}  # adiciona preços 
        data.update(users)  
        
        with open(config.DATA_FILE, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
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
            session_active.clear()  #avisa as outras threads
            break                   #sai do loop antes do if not message


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
                        # Verifica se o ativo ainda existe nos preços atuais antes de acessar
                        if asset in prices:
                            total_value = qtd * prices[asset]
                            text += f"[{asset}]: {qtd} unidades (Total: R${total_value:.2f})\n"

                        else:
                            # Ativo foi removido do config mas ainda está no portfólio do usuário
                            text += f"[{asset}]: {qtd} unidades (preço indisponível)\n"

                text += "\n---------------------------\n"
            client_socket.send(text.encode())

########################## implemntando buywhen ####################
        elif message.lower().startswith(":buywhen"):  # ← antes do :buy
            parts = message.split()
            if len(parts) == 4:
                asset = parts[1].upper()
                try:
                    qty = int(parts[2])
                    target_price = float(parts[3])
                except ValueError:
                    client_socket.send("[ERROR] Uso: :buywhen <ATIVO> <QTD> <PRECO>".encode())
                    continue
 
                with mutex:
                    if asset not in prices:
                        response = f"[ERROR] Ativo '{asset}' não encontrado."
                    elif username in pending_orders and asset in pending_orders[username]:
                        response = f"[ERROR] Já existe uma ordem pendente para {asset}."
                    else:
                        reserved = target_price * qty
                        if users[username]['balance'] < reserved:
                            response = f"[ERROR] Saldo insuficiente para reservar R${reserved:.2f}."
                        else:
                            users[username]['balance'] -= reserved    
                            if username not in pending_orders:
                                pending_orders[username] = {}
                            pending_orders[username][asset] = {
                                "qty": qty,
                                "target_price": target_price,
                                "socket": client_socket,
                                "reserved": reserved
                            }
                            save_users()
                            response = (f"[OK] Ordem registrada: comprar {qty}x {asset} "
                                        f"quando atingir R${target_price:.2f} ")

                client_socket.send(response.encode())
            else:
                client_socket.send("[ERROR] Uso: :buywhen <ATIVO> <QTD> <PRECO>".encode())
####################################################################

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
            client_socket.send("\n[ERROR] Comando não reconhecido. Use :buy, :sell, :buywhen, :carteira, :exit".encode())

    session_active.clear()

######################
##  Thread do feed  ##
######################

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
    
    last_save = time.time()
     
    while server_running.is_set():

        with mutex:

            for asset in prices:

                variation = random.uniform(-tick * var_tick, tick * var_tick)
                prices[asset] = round(prices[asset] + variation, 2)
 
                if prices[asset] < min_price:
                    prices[asset] = min_price

###################### Checa ordens pendentes################
            
            to_remove = []
            needs_save = False
            for uname, orders in pending_orders.items():
                for asset, order in list(orders.items()):


                    if prices[asset] <= order['target_price']:
                        # Preço atingido — executa a compra
                        actual_cost = prices[asset] * order['qty']
                        users[uname]['portfolio'][asset] += order['qty']
                        diff = order['reserved'] - actual_cost
                        if diff > 0:  # Preço caiu abaixo do alvo — devolve diferença
                            users[uname]['balance'] += diff
                        needs_save = True
                        msg = (f"\n[OK] Ordem executada: COMPRA {order['qty']}x {asset} "
                               f"a R${prices[asset]:.2f} | Total: R${actual_cost:.2f}")
                        if diff > 0:
                            msg += f" | Diferença devolvida: R${diff:.2f}"
                        try:
                            order['socket'].send(msg.encode())
                        except OSError:
                            pass
                        to_remove.append((uname, asset))

            for uname, asset in to_remove:
                del pending_orders[uname][asset]

#############################################################
        if needs_save:
            save_users()
        
        if time.time() - last_save >= 30:
            save_users()
            last_save = time.time()

        
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
    msg += "-------------------------------------------\nComandos: :buy <ATIVO> <QTD> | :sell <ATIVO> <QTD> | :buywhen <ATIVO> <QTD> <PRECO> | :carteira | :exit\n-------------------------------------------\n"
    
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
        target = feed_sender, #envia as cotações periodicamente para o cliente via socket
        args=(client_socket, username, session_active),
        name=f"SvTh2Pricing-{address}")
    
    SvTh1Commands.daemon = True
    SvTh2Pricing.daemon = True #daemon faz com que thread encerre junto com o main
    
    SvTh1Commands.start()
    SvTh2Pricing.start()

    SvTh1Commands.join() # main vai travar até a thread de comandos fechar

    session_active.clear()

    with mutex:
        if username in pending_orders and pending_orders[username]:
            for asset, order in pending_orders[username].items():
                # Devolve o saldo que estava reservado para cada ordem
                users[username]['balance'] += order['reserved']
                print(f"[INFO] Ordem cancelada na desconexão: {order['qty']}x {asset} — saldo de R${order['reserved']:.2f} devolvido a {username}.")
            del pending_orders[username]  # remove todas as ordens do usuário
            save_users()

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

    except OSError as e:        #Cobre falhas inesperadas no accept() e no socket do servidor
        print(f"\n[ERROR] Erro no servidor: {e}")

    finally:    #ele sempre sera executado mesmo com erros
                # garante que os dados sejam salvos e o socket fechado
        with mutex:
                save_users()
        print("[INFO] Dados salvos. Servidor encerrado.")

        server_socket.close()

main()

