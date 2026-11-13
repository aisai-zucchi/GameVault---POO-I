# GameVault

GameVault é um projeto acadêmico de Programação Orientada a Objetos em Python.
O sistema mantém um catálogo de jogos físicos e digitais, categorias, exemplares
e membros, além de registrar empréstimos e devoluções em memória.

Repositório: [aisai-zucchi/GameVault---POO-I](https://github.com/aisai-zucchi/GameVault---POO-I)

## Funcionalidades

- CRUD e consultas de jogos físicos e digitais;
- cadastro e consulta de categorias, membros e exemplares;
- associação de jogos a categoria e plataforma;
- controle de disponibilidade dos exemplares físicos;
- registro de empréstimos com histórico e data de devolução;
- devolução com liberação do exemplar;
- bloqueio de exclusão de jogos com exemplar emprestado;
- fachada `SistemaGameVault` para integrar catálogo, membros e empréstimos.

## Regras de negócio

- **RN01 - disponibilidade:** somente um exemplar físico disponível e sem outro
  empréstimo ativo pode ser emprestado.
- **RN02 - limite do membro:** cada membro pode manter no máximo três
  empréstimos ativos ao mesmo tempo.

Uma devolução não aceita data anterior ao início. Empréstimos finalizados
permanecem no histórico, e o mesmo exemplar pode gerar um novo registro depois
de devolvido.

## Conceitos de POO

- **Abstração e herança:** `Jogo` usa `ABC` e `@abstractmethod`;
  `JogoFisico` e `JogoDigital` especializam a classe abstrata.
- **Polimorfismo:** cada tipo de jogo implementa `resumo_disponibilidade()` com
  um comportamento próprio.
- **Encapsulamento:** atributos internos usam `_atributo`, propriedades de
  leitura e métodos que validam alterações.
- **Composição e agregação:** o catálogo mantém objetos `Jogo` e `Categoria`, o
  jogo físico mantém objetos `Exemplar`, e os serviços mantêm membros e
  empréstimos.
- **Associação:** cada `Emprestimo` referencia diretamente os objetos `Membro` e
  `Exemplar`, preservando o histórico das relações.

## Estrutura

```text
gamevault/
|-- __init__.py                 # API pública
|-- sistema.py                  # Fachada de integração
|-- modelos/
|   |-- categoria.py
|   |-- emprestimo.py
|   |-- exemplar.py
|   |-- jogo.py
|   `-- membro.py
`-- servicos/
    |-- cadastro_membros.py
    |-- catalogo.py
    `-- gestor_emprestimos.py
tests/
|-- test_gamevault.py           # Fluxos integrados e regras RN01/RN02
|-- test_main.py
|-- test_modelos.py
`-- test_servicos.py
main.py                         # Demonstração completa pelo terminal
```

## Requisitos

- Python 3.10 ou mais recente;
- nenhuma dependência externa.

## Executar a demonstração

Na raiz do repositório:

```bash
python -B main.py
```

A demonstração cria as classes principais, exibe o catálogo de forma
polimórfica, atualiza um jogo, registra empréstimos, comprova os bloqueios de
RN01 e RN02, realiza devoluções, preserva o histórico e valida a exclusão.

## Executar os testes

```bash
python -B -m unittest discover -s tests -v
```

Os testes cobrem modelos, encapsulamento, CRUD, categorias, consultas,
polimorfismo, empréstimos, devoluções, RN01, RN02, integração do sistema e a
demonstração do terminal.

## Escopo da entrega

Este estado corresponde à segunda entrega do projeto. A interface Tkinter e os
itens da terceira entrega não fazem parte deste código.
