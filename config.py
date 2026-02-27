# Pra deixar as variáveis globais

HOST = 'localhost'
PORT = 5000 # Porta de endereço pro server

USER_BALANCE = 10000.00 # Como pedido nas especificações ("atualizando o saldo e a carteira do usuário em memória compartilhada")

INITIAL_ASSETS = { # Peguei os valores dos mais negociados (dia 27/02/26)
    "PETR4": 39.61,
    "BBDC4": 20.98,
    "POMO4": 7.04,
    "RAIZ4": 0.650,
    "CSAN3": 6.64 
}

TICK_SIZE = 0.01 # Do mercado à vista da B3
MAX_TICKS_PER_VARIATION = 10
MIN_TICK_TIME = 1 # Tempo mínimo para alteração de preço
MAX_TIME_TICK = 3 # Tempo máximo para alteração de preço
FEED_INTERVAL = 5 # Feed constante de preços que o servidor vai mandar pro cliente
MIN_PRICE = 0.01 # Menor valor possível



