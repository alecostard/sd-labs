# Servidor que conta ocorrências de palavras
## Uso
Em um terminal, execute o servidor
``` python
$ python server.py
```

Em seguida, em outro terminal, execute o cliente
``` python
$ python client.py
```

Esse servidor é capaz de servir múltiplos clientes de forma concorrente. Além disso, caso seja digitado `fim` na linha de comando do servidor ele deixará de aceitar novas conexões e encerrará quando os serviços em andamento terminarem.