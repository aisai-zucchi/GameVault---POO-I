# GameVault

O GameVault e um projeto didatico de Programacao Orientada a Objetos para
catalogar jogos fisicos e digitais, controlar exemplares e cadastrar membros.

## Estrutura

```text
gamevault/
|-- modelos/          # Entidades do dominio
|   |-- categoria.py
|   |-- exemplar.py
|   |-- jogo.py
|   `-- membro.py
`-- servicos/         # Cadastro e organizacao das entidades
    |-- cadastro_membros.py
    `-- catalogo.py
tests/                # Testes automatizados
main.py               # Exemplo executavel
```

O projeto usa somente a biblioteca padrao do Python e requer Python 3.10 ou
mais recente.

## Executar

```bash
python main.py
```

## Testar

```bash
python -m unittest discover -s tests -v
```

## Escopo atual

- categorias com renomeacao;
- exemplares fisicos com controle de disponibilidade;
- jogos fisicos e digitais;
- catalogo de jogos;
- membros com limite de tres emprestimos ativos;
- cadastro e consulta de membros.

O fluxo completo de emprestimos, as datas de devolucao e uma interface para o
usuario ainda serao implementados em etapas futuras.
