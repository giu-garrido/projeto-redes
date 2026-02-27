# Projeto Prático 1 - Pregão da Bolsa de Valores

Simulação de um ambiente de negociação de ativos em tempo real, desenvolvido como projeto prático da disciplina de Redes e Comunicação - PUC-Campinas (CD&IA).

**Grupo Jammers**

---

## Sobre o projeto

Sistema cliente/servidor usando sockets TCP e threads onde o usuário atua como um trader. O servidor simula a oscilação de preços de ações reais da B3, enquanto o cliente envia ordens de compra e venda e recebe atualizações em tempo real.

**Funcionalidades**

- Conexão TCP bidirecional assíncrona via threads
- Feed automático de cotações a cada 5 segundos (push do servidor)
- Oscilação de preços baseada no tick size da B3 (R$ 0,01)
- Compra e venda de ativos com controle de saldo e carteira
- Memória compartilhada protegida por mutex (lock)

---

## Estrutura do Repositório

projeto-redes/
├── README.md
├── config.py &emsp;&emsp;# constantes (host, porta, ativos, parâmetros de simulação)
├── server.py &emsp;&emsp;# lógica do servidor (processamento de ordens + simulação)
├── client.py &emsp;&emsp;# interface do cliente (input do usuário + exibição do feed)
└── docs/ &emsp;&emsp;# material de estudo e documentação
&emsp;&emsp;&emsp;└── pseudocodigo_pregao.md

---

## Comandos

| Comando               | Descrição                         |
|-----------------------|-----------------------------------|
| `:buy <ATIVO> <QTD>`  | Compra X unidades de um ativo     |
| `:sell <ATIVO> <QTD>` | Vende X unidades de um ativo      |
| `:carteira`           | Exibe saldo e ativos na carteira  |
| `:exit`               | Encerra a conexão                 |

---

## Como executar

**Requisitos:** Python 3.x

1. Abra um terminal e inicie o servidor:

```bash
python server.py
```

2. Em outro terminal, inicie o cliente:

```bash
python client.py
```

3. No cliente, utilize os comandos para interagir com o sistema.

---
