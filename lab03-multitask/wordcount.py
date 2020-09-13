import re
from collections import Counter

### Camada de acesso aos dados ###


def data_access(filename):
    """Retorna o resultado de filename como uma string."""
    with open(filename, 'r') as file:
        result = file.read()
    return result


### Camada de processamento ###


def file_words(filename):
    """Retorna o conteúdo do arquivo filename como uma lista de palavras."""
    contents = data_access(filename)
    return [word.lower() for word in re.findall(r'\w+', contents)]


def top_words(filename):
    """Retorna uma lista de tuplas (palavra, ocorrencias) para filename."""
    return Counter(file_words(filename)).most_common(10)
