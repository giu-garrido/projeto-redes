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

[08:34] Giulia M. Garrido

- Corrigi erro de identação no server, que fazia que as atualizações de preço não aparecessem para o client