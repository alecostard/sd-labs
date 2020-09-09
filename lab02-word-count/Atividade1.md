# Camadas

## Interface com usuário
- recebe nome do arquivo.
- exibe o resultado:
    - lista de palavras com suas ocorrências.
    - mensagem de erro dizendo que o arquivo não foi encontrado.
    - **recebe da camada de processamento a lista de resultadas já processada.**


## Camada de processamento
- solicita acesso ao arquivo texto.
- caso o arquivo seja válido:
    - realiza a contagem de palavras.
    - **envia para a camada de interface a lista de palavras. Essa lista possui as seguintes propriedades:**
        - a lista possui tamanho máximo 10.
        - cada elemento é um par ordenado com a estrutura (palavra, ocorrências).
        - a lista está ordenada de forma descrescente por ocorrência das palavras no arquivo texto.
- responde com erro caso o arquivo seja inválido.

## Camada de acesso aos dados
- envia o conteúdo do arquivo caso ele exista
- reporta erro caso o arquivo não exista