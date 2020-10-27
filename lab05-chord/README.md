# Tabela hash distribuída usando uma simplificação do Chord

## Uso
Inicie a rede com os processos que participarão do anel e o servidor de endereços para essa rede.

    $ python chord_start.py

Será necessário digitar um parâmetro `n` inteiro para a rede, que terá `2^n` nós.

Inicie o cliente

    $ python client.py

No cliente, execute as inserções e buscas.

    $ insere(1, oi, tudo bem?)
    $ insere(0, alo, alo)
    $ busca(1, 1, oi)
    $ busca(2, 0, oi)

Para que seja possível acompanhar o funcionamento da rede, o programa que inicia a rede está mostrando na tela as informações das mensagens trocadas na rede do Chord.