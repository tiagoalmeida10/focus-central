
# Focus Central

Sistema web para gerenciamento e acompanhamento de chamados técnicos da Focus Network.

## Objetivo

Centralizar o registro e acompanhamento de solicitações de suporte técnico, permitindo organizar chamados, acompanhar prioridades, responsáveis, status e prazos de atendimento (SLA).

## Tecnologias utilizadas

- Python 3.12
- Django 5.2
- PostgreSQL 18
- HTML5
- CSS3
- Bootstrap 5.3

## Funcionalidades

- Autenticação de usuários.
- Dashboard com indicadores de chamados.
- Cadastro e gerenciamento de clientes.
- Abertura e consulta de chamados.
- Filtros por status e prioridade.
- Atribuição de responsáveis.
- Histórico de alterações e comentários.
- Controle de prazos de SLA.

## Estrutura do projeto

- `config/`: configurações principais do Django.
- `usuarios/`: gerenciamento de usuários e autenticação.
- `clientes/`: cadastro e gerenciamento de clientes.
- `chamados/`: gerenciamento de chamados e regras de SLA.
- `templates/`: páginas HTML do sistema.

## Execução em ambiente de desenvolvimento

1. Clone o repositório:

   `git clone https://github.com/tiagoalmeida10/focus-central.git`

2. Acesse a pasta:

   `cd focus-central`

3. Crie e ative um ambiente virtual:

   `python -m venv .venv`

4. Instale as dependências:

   `pip install django psycopg[binary] python-dotenv`

5. Configure as variáveis de ambiente no arquivo `.env`, incluindo as credenciais do PostgreSQL e a chave secreta do Django.

6. Execute as migrações:

   `python manage.py migrate`

7. Crie um usuário administrativo:

   `python manage.py createsuperuser`

8. Inicie o servidor:

   `python manage.py runserver`

9. Acesse:

   `http://127.0.0.1:8000/`

## Repositório

https://github.com/tiagoalmeida10/focus-central
