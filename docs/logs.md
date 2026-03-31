## Template

*Template para vocês alterarem conforme usarem*

### [08/03/26]

[19:32] Giulia M. Garrido

- Corrigi uma pequena confusão no client.py, onde as funções recebiam o argumento server_socket, mas na função usavam client_socket
- Troquei os nomes de client_socket para server_socket na main() em client.py para fins de correção
- Dei sequência à função dos comandos em server.py
- Adicionei a flag *active* em config.py para que as thread 2 pare de funcionar assim que a thread 1 parar
- Terminei a função dos comandos no lado do servidor.
- Corrigi para que a função do feed utilizasse variáveis globais

### [09/03/26]

[17:14] Giulia M. Garrido

- Corrigi erro de identação no server, que fazia que as atualizações de preço não aparecessem para o client
- Corrigi erro meu, que fazia com que as duas funções do client chamarem *recv()* no mesmo socket. Aí o feedup recebia a mensagem de confirmação de compra (exemplo) e o negotiator ficasse esperando. Se o servidor mandasse a atualização do feed, quem recebia era o negotiator. (muita confusão com uma só linha de código)
-  Corrigi questão do tempo, que agora utiliza time.time pra pegar o tempo real atual pra calcular o tempo atual - de quando começou o processo (ou terminou o anterior)
-  Adicionei o thread join() que tava faltando em um dos arquivos ( não lembro mais qual era B) )

 ### [22/03/26]

 [16:00] Vitor R. A. Furuta
- Correções de lógica em market_sim onde eram usadas ordens erradas e nomes de variáveis que nunca eram alterados/chamados.
- Implementação de max_clients para controle póstumo de acesso.
- Mudanças na main para permitir múltiplos users.
- Conteúdo da main que interagia com o user foi separado em outra função (client_waiter), para dinamizar e expandir interações server-user.
- Adição de controle de usernames, agora são únicos, são perguntados ao tentar acesso e já são chamados na criação da thread dedicada.

 ### [23/03/26]
 [15:20] Vitor R. A. Furuta
 - Refatoração do uso de balance e portfolio, antes eram travados a single-user, agora adaptado para multi-user com acesso em users[username]['balance'] e users[username]['portfolio']
 - Troca das variáveis antigas pelo novo modelo
 - Alteração no valor inicial de carteira, de 10000 para 1000

[20:00] Giulia M. Garrido
- Separei a função market_simulator entre uma só função para simular o mercado e outra para enviar as infos para os clientes
- Flag active global removida, agora cada sessão tem threading.Event()
- SO_REUSEADDR no server pra parar de dar "Address already in use"
- Faltava global clients_connected no main()
- Salva saldo e carteira em users_data.json, carrega de volta quando o server reinicia
- Taquei-lhe uns try/except

[22:30] Victor M. Franca
- Bugs corrigidos:
    - Thread 2 iniciava market_simulation que já está rodando globalmente, entao alterei para feed_sender, que envia as cotações periodicamente para o cliente via socket
    - fluxo na função commands, codigo nao finalizava o loop, entao adicionei: session_active.clear(que avisa as outras threads) e um break. 
- Criacao da variavel TIMEOUT_TIME para definir quanto tempo de expedição para ordem do usuario (necessaria para implentar ordem de compra por preco especifico)
- Criacao do dicionario global pending_orders = {} no server.py

 ### [24/03/26]
[9:30] Victor M. Franca
- Implentando comando :buywhen; 
    - valida se o ativo existe, se não há outra ordem pendente para aquele ativo, e se o usuário tem saldo suficiente
    - reserva o saldo, desconta o valor do saldo imediatamente para garantir que o dinheiro existe na hora da compra
    - registra a ordem no dicionário "pending_orders" com todas as informações necessárias: quantidade, preço-alvo, horário de expiração e o socket do cliente
    - exemplo de como usar: ":buywhen PETR4 2 38.50"
- Implentando verificação dentro do market_simulation,
    - Preço atingiu o alvo → executa a compra, adiciona os ativos na carteira, devolve a diferença caso o preço tenha caído abaixo do alvo, e notifica o cliente
    - Ordem expirou → devolve o saldo reservado e notifica o cliente

 ### [28/03/26]
[16:00] Victor M. Franca

- att no .client:
    - Adiconando sys no import,necessario para o sys.exit() 
    - Adicionando .close e sys.exit no primeiro do try except do main, para encerrar de forma limpa (linha 74)
    - Login agora e protegido por um try except 

- att no .server:
    - Visando impedir que erros afetem o salvando e fechamento do socket
        - adicionando um "except OSError", cobre as falahas do accept e do socket (linha 476)
        - adicionando um "finally" para garantir que os dados sejam salvos e o socket fechado (linha 479)
    - KeyError que poderia dar no :carteira protegido, so adicionei um if pra evitar o KeyError caso o Ativo n exista. (linha 95)
 
 ### [30/03/26]
[18:00] Vitor R. A. Furuta
- users_data.json -> data.json
- Adição de persistência nos valores dos preços, o último valor atualizado agora é salvo em data.json.
- Preços alterados serão salvos junto aos eventos, caso não haja eventos -> salva a cada 30s.
- Adição de daemon na thread de comandos. Corrige necessidade de 2 CTRL+C para encerrar programa.

[21:00] Victor M. Franca
- Removendo o Timeout para ordem de compra, estava apresentado bugs e como não é um requisito optamos por remover
- corrigindo bug do buywhen



