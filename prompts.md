# Uso de IA no projeto (copiloto)

A IA generativa foi usada como **copiloto de desenvolvimento**: a equipe definiu o problema,
o modelo de domínio, a regra de risco e o contrato REST (ver Ficha da CitizenTech) e revisou,
executou e ajustou todo o código gerado. Nenhum dado real de pessoas foi enviado à IA.

## Principais prompts

1. **Arquitetura**
   > "Monte uma API REST em Python com FastAPI, SQLAlchemy 2.x (Mapped[]), Alembic e Pydantic v2
   > para o projeto Alerta Córrego, em camadas: domain, models, schemas, repositories, services e
   > api/routes. Siga exatamente este modelo de domínio e estes endpoints: (ficha colada)."

2. **Regra de domínio**
   > "Implemente classificar_risco como função pura, sem dependência de framework, com a regra:
   > nível >= crítico → CRITICO; >= alerta → ALERTA; >= 75% do alerta ou chuva >= 30 mm/h →
   > ATENCAO; senão NORMAL. Escreva testes pytest cobrindo os 4 níveis e os valores de fronteira."

3. **Caso de uso central**
   > "Ao registrar uma leitura ALERTA ou CRITICO, crie um Alerta para o córrego e retorne os
   > moradores prioritários. Não registre dados pessoais de moradores em log."

4. **Migrações e seed**
   > "Crie migrações Alembic explícitas: 0001 cria as tabelas, 0002 insere 2 córregos, 2 sensores,
   > 6 moradores fictícios (3 prioritários) e algumas leituras. Funcione em SQLite e PostgreSQL."

5. **Testes**
   > "Escreva testes com TestClient usando SQLite em memória (StaticPool) e dependency_overrides,
   > cobrindo criação, 404, 422 e a geração de alerta em leitura crítica."

6. **Documentação**
   > "Escreva o README em português com ficha, arquitetura (mermaid), modelo de dados (erDiagram),
   > como rodar, tabela de endpoints, exemplos curl e seção de evidências."

## O que a equipe validou manualmente
- Regra de risco conferida com a ficha (mesma regra usada no app Mobile e na API C#).
- Execução de `alembic upgrade head`, `pytest` e testes manuais no Swagger (`/docs`).
- Revisão de privacidade: dados fictícios, sem CPF, sem dados pessoais em log.
