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