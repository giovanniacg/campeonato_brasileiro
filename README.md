# Campeonato Brasileiro

## Requisitos
 - Python 3.14 ou superior
 - [UV](https://github.com/astral-sh/uv) (opcional, recomendado para gerenciamento de dependências)

## Instalação das dependências

### Usando UV (recomendado)
```sh
uv sync dev
```

### Usando pip (Python puro)
```sh
python -m pip install -r requirements.txt
```

## Executando os testes

### Todos
```sh
pytest
```

### De um modelo específico
```sh
pytest matches/
pytest clubs/
pytest leagues/
```

## Observações
 - Certifique-se de estar usando Python 3.14 ou superior.
