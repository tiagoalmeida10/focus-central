# Revisão Técnica — Focus Central

## 1. Arquitetura

O Focus Central utiliza uma arquitetura monolítica em camadas, desenvolvida com Django. A separação das funcionalidades em aplicações específicas (`usuarios`, `clientes` e `chamados`) facilita a organização e a manutenção do código.

As responsabilidades estão distribuídas entre modelos, formulários, visualizações, rotas e templates, favorecendo a separação de responsabilidades.

## 2. Refatoração e legibilidade

Foi adotada a organização das funcionalidades em módulos independentes, evitando concentrar toda a lógica em um único arquivo.

As regras de cálculo de SLA foram separadas no módulo `sla.py`, permitindo reutilização e facilitando a realização de testes automatizados.

Como oportunidade de melhoria, recomenda-se avaliar futuramente a centralização das regras de histórico e atualização dos chamados, reduzindo responsabilidades concentradas no método `save()` do modelo.

## 3. Segurança

O sistema utiliza autenticação de usuários para proteger as páginas operacionais por meio do mecanismo `login_required` do Django.

Os formulários utilizam proteção CSRF, e as configurações sensíveis são mantidas em variáveis de ambiente, evitando a exposição direta de credenciais no código-fonte.

Como melhoria futura, recomenda-se revisar as permissões de acesso por funcionalidade e manter as configurações de produção com `DEBUG=False`.

## 4. Testes e qualidade

Foram implementados testes automatizados para validar:

- Cálculo dos prazos de SLA dentro do expediente.
- Cálculo de prazos que ultrapassam o expediente.
- Desconsideração dos finais de semana.
- Abertura de chamados.
- Atualização de status e atribuição de responsáveis.
- Registro de comentários no histórico.

Os seis testes automatizados foram executados com sucesso.

## 5. Conclusão

A revisão identificou uma estrutura organizada, com separação de responsabilidades e funcionalidades principais implementadas.

Foram identificadas oportunidades de evolução relacionadas à centralização das regras de negócio, ampliação dos testes e revisão das permissões de acesso.

O projeto apresenta uma base adequada para a continuidade do desenvolvimento do MVP Focus Central.