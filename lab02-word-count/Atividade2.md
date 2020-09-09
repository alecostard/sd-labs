# Arquitetura de sistema

## Cliente
- implementa a camada de interface com o usuário.
- em uma única execução pode ser solicitado o processamento de diversos arquivos.

## Servidor
- implementa as camadas de processamento e acesso aos dados.
- trata um cliente de cada vez.
- espera novas conexões após servir um cliente.

## Mensagens
O cliente e o servidor se comunicam através de mensagens implementadas como uma estrutura com dois campos: *tipo* e *conteúdo*.

## Tipos de mensagens usados
### Enviadas pelo cliente
- { tipo: ordena palavras, conteúdo: nome do arquivo }
- { tipo: encerra conexão, conteúdo: vazio }

### Enviadas pelo servidor
- { tipo: sucesso, conteúdo: lista com 10 palavras mais frequentes }
- { tipo: erro, conteúdo: nome de arquivo inválido }
- { tipo: erro, conteúdo: arquivo inexistente }
- { tipo: erro, conteúdo: mensagem recebida não suportada }

## Exemplos de trocas de mensagens previstas
### Operação bem sucedida
- c: { tipo: ordena palavras, conteúdo: nome do arquivo }
- s: { tipo: sucesso, conteúdo: lista com 10 palavras mais frequentes }
- c: { tipo: encerra conexão, conteúdo: vazio }

### Arquivo inexistente
- c: { tipo: ordena palavras, conteúdo: nome do arquivo }
- s: { tipo: erro, conteúdo: arquivo inexistente }
- c: { tipo: encerra conexão, conteúdo: vazio }
 
## Decisões de implementação
Para a implementação dessa atividade, foi assumido que os arquivos estão no servidor.