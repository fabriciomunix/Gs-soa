# Alerta Córrego — API SOA (FastAPI)

> FIAP · Global Solution · **Arquitetura Orientada a Serviços (SOA) e Web Services**

## Ficha da CitizenTech — Alerta Córrego

| Campo | Preenchimento |
|---|---|
| **Nome da CitizenTech** | Alerta Córrego |
| **Cidade e bairro** | São Paulo — M'Boi Mirim (Zona Sul) |
| **Cidadão beneficiado** | Morador de rua às margens de córrego com risco de alagamento, com prioridade para idosos e pessoas com mobilidade reduzida |
| **Problema, em uma frase** | Moradores de ruas às margens de córregos pequenos recebem o alerta de chuva da Defesa Civil para a região inteira, mas não sabem quando o córrego da rua deles vai transbordar, e quem tem mobilidade reduzida depende de vizinhos para sair a tempo. |
| **Como funciona** | Um ESP32 no córrego mede o nível da água e a chuva e publica via MQTT. Um servidor Linux recebe as leituras, classifica o risco (Normal / Atenção / Evacuar) e mostra um painel web com a rede de apoio aos moradores prioritários. Um modelo de ML antecipa temporais, e os dados sensíveis dos moradores são auditados e protegidos. |
| **Diferencial** | Complementa a Defesa Civil: o alerta oficial avisa que vai chover na região; o Alerta Córrego avisa que a água está subindo naquela rua e quem precisa de ajuda primeiro. |
| **O que cada parte faz** | **Physical Computing:** estação ESP32 no Wokwi (nível do córrego, chuva, LEDs, sirene, LCD, MQTT) · **Operating Systems:** servidor Linux provisionado por Shell Script, monitorado e tolerante a falhas, que hospeda o painel · **IA & ML:** XGBoost que prevê chuva forte nas próximas 3 h para antecipar o alerta · **Cybersecurity:** CitizenGuard, que detecta dados pessoais e sensíveis, rastreia vazamentos (taint analysis), traduz falhas em alertas por IA e mede o Risco Cidadão |
| **Link do repositório** | **SOA (este repositório): https://github.com/fabriciomunix/Gs-soa** · Mobile: https://github.com/fabriciomunix/GS-Mobile · C#: https://github.com/fabriciomunix/Gs-c- · QA: https://github.com/fabriciomunix/GS-QA |
| **Indicador de impacto** | Minutos de antecedência entre o alerta e o transbordamento; nº de moradores prioritários alertados; Risco Cidadão dos dados cadastrados |
| **ODS conectados** | ODS 11 (cidades resilientes, meta 11.5) · ODS 13 (adaptação ao clima, meta 13.1) · ODS 10 (inclusão de idosos e PcD) |

### Integrantes
- Fabricio Carlos Duarte Rossi Junior — RM 555017
- Arnaldo Filho — RM 555780

---

## Descrição da solução

O **Alerta Córrego** monitora córregos pequenos da Zona Sul de São Paulo que não têm estação
oficial. Um sensor **ESP32** instalado no córrego envia, periodicamente, o nível da água (cm) e a
chuva (mm/h) para esta **API REST**. A API:

1. **registra a leitura** no banco de dados;
2. **classifica o risco** (`NORMAL`, `ATENCAO`, `ALERTA`, `CRITICO`) com base nos limites do córrego;
3. quando o risco é **ALERTA** ou **CRITICO**, **cria um Alerta** para o córrego e devolve a
   **lista de moradores prioritários** (idosos, cadeirantes, acamados) que precisam de ajuda para sair;
4. expõe status, histórico e alertas para o **app Mobile** do morador e para o painel web.

### Regra de classificação de risco (mesma no Mobile, SOA e C#)

| Condição (avaliada nesta ordem) | Risco |
|---|---|
| nível ≥ `nivelCriticoCm` | **CRITICO** |
| nível ≥ `nivelAlertaCm` | **ALERTA** |
| nível ≥ 0,75 × `nivelAlertaCm` **ou** chuva ≥ 30 mm/h | **ATENCAO** |
| caso contrário | **NORMAL** |

Implementada como função pura em [`app/domain/risco.py`](app/domain/risco.py), sem dependência de
framework, e coberta por testes de fronteira em [`tests/test_risco.py`](tests/test_risco.py).

### Outras regras de negócio
- `nivelCriticoCm` deve ser maior que `nivelAlertaCm` (validação no schema, no serviço e `CHECK` no banco).
- Morador com `tipoNecessidade` diferente de `NENHUMA` é sempre **prioritário**.
- Sensor inativo não pode registrar leituras (422); código de sensor é único (409).
- Alerta encerrado não pode ser encerrado novamente (409).
- **Privacidade:** dados de moradores são **fictícios**, sem CPF; os logs registram apenas IDs e
  contagens, nunca nome/telefone/endereço.

---

## Arquitetura

Arquitetura em camadas (clean/layered), cada camada só conhece a de baixo:

```mermaid
flowchart TD
    ESP[Sensor ESP32] -->|POST /api/leituras| API
    APP[App Mobile / Painel Web] -->|REST JSON camelCase| API
    subgraph API[FastAPI - app/]
        R[api/routes<br/>routers, status HTTP, Swagger] --> S[services<br/>casos de uso e regras]
        S --> D[domain<br/>enums + classificar_risco puro]
        S --> RP[repositories<br/>consultas SQLAlchemy]
        R -.-> SC[schemas<br/>Pydantic v2 camelCase]
        RP --> M[models<br/>ORM SQLAlchemy 2.x]
    end
    M --> DB[(SQLite / PostgreSQL)]
    MIG[Alembic migrations] --> DB
```

```
soa/
├── app/
│   ├── main.py               # FastAPI: título, descrição, tags, CORS, handlers de erro
│   ├── core/                 # config (DATABASE_URL, CORS) e exceções de negócio
│   ├── db/                   # Base declarativa, engine, SessionLocal, get_db
│   ├── domain/               # NivelRisco, TipoNecessidade, classificar_risco (puro)
│   ├── models/               # Corrego, Sensor, Leitura, Morador, Alerta (Mapped[])
│   ├── schemas/              # Create/Update/Read com validação e alias camelCase
│   ├── repositories/         # acesso a dados
│   ├── services/             # regras: registrar leitura, gerar alerta, 404/409/422
│   └── api/routes/           # um router por recurso
├── alembic/                  # env.py + versions/0001_criar_tabelas, 0002_seed_dados
├── tests/                    # pytest + TestClient (SQLite em memória)
├── docs/evidencias/          # prints do Swagger, testes e banco
├── docker-compose.yml        # PostgreSQL opcional
└── requirements.txt
```

Fluxo do caso de uso principal (`POST /api/leituras`):

```mermaid
sequenceDiagram
    participant E as ESP32
    participant R as Router leituras
    participant S as LeituraService
    participant D as domain.classificar_risco
    participant DB as Banco
    E->>R: POST /api/leituras {sensorId, nivelAguaCm, chuvaMmHora}
    R->>S: registrar(dados)
    S->>DB: busca sensor + córrego (404 se não existir)
    S->>DB: grava Leitura
    S->>D: classificar_risco(nível, chuva, limites)
    D-->>S: CRITICO
    S->>DB: grava Alerta + busca moradores prioritários
    S-->>R: leitura + nivelRisco + alerta + moradoresPrioritarios
    R-->>E: 201 Created
```

---

## Modelo de dados

```mermaid
erDiagram
    CORREGOS ||--o{ SENSORES : possui
    SENSORES ||--o{ LEITURAS : registra
    CORREGOS ||--o{ MORADORES : "tem às margens"
    CORREGOS ||--o{ ALERTAS : gera

    CORREGOS {
        int id PK
        string nome
        string bairro
        float latitude
        float longitude
        float nivel_alerta_cm
        float nivel_critico_cm
    }
    SENSORES {
        int id PK
        string codigo UK
        int corrego_id FK
        bool ativo
        datetime instalado_em
    }
    LEITURAS {
        int id PK
        int sensor_id FK
        float nivel_agua_cm
        float chuva_mm_hora
        datetime registrada_em
    }
    MORADORES {
        int id PK
        string nome
        string telefone
        string endereco
        int corrego_id FK
        bool prioritario
        string tipo_necessidade
        datetime criado_em
    }
    ALERTAS {
        int id PK
        int corrego_id FK
        string nivel_risco
        string mensagem
        float nivel_agua_cm
        datetime criado_em
        bool ativo
    }
```

No banco as colunas usam `snake_case`; na API o JSON usa `camelCase` (`nivelAlertaCm`,
`corregoId`, ...) via `alias_generator` do Pydantic. Chaves estrangeiras usam `ON DELETE CASCADE`.

---

## Como rodar

Pré-requisito: **Python 3.11+** (compatível com Python 3.11–3.13).

```bash
# 1. Clonar
git clone https://github.com/fabriciomunix/Gs-soa.git
cd Gs-soa

# 2. Ambiente virtual
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# 3. Dependências
pip install -r requirements.txt

# 4. Criar tabelas + dados de exemplo (migrações Alembic)
alembic upgrade head

# 5. Subir a API
uvicorn app.main:app --reload
```

Abra:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **OpenAPI JSON:** http://127.0.0.1:8000/openapi.json

### Banco de dados
- Padrão: **SQLite** em `./alerta_corrego.db` (nada a configurar).
- **PostgreSQL** (opcional):
  ```bash
  docker compose up -d
  # Linux/macOS
  export DATABASE_URL=postgresql+psycopg2://alerta:alerta@localhost:5432/alerta_corrego
  # Windows (PowerShell)
  $env:DATABASE_URL="postgresql+psycopg2://alerta:alerta@localhost:5432/alerta_corrego"
  alembic upgrade head
  uvicorn app.main:app --reload
  ```

### Migrações (Alembic)
| Revisão | Conteúdo |
|---|---|
| `0001_criar_tabelas` | Cria `corregos`, `sensores`, `leituras`, `moradores`, `alertas` com FKs, índices e `CHECK` |
| `0002_seed_dados` | 2 córregos (Ponte Baixa — M'Boi Mirim; Morro do S — Campo Limpo), 1 sensor cada, 6 moradores fictícios (3 prioritários), 5 leituras e 1 alerta ativo |

```bash
alembic upgrade head        # aplica tudo
alembic downgrade -1        # remove o seed
alembic downgrade base      # remove as tabelas
alembic history             # lista revisões
```

---

## Como rodar os testes

```bash
pytest
```

Os testes usam **SQLite em memória** (`StaticPool`) e `dependency_overrides` do FastAPI, então
não tocam no banco real.

| Arquivo | O que cobre |
|---|---|
| `tests/test_risco.py` | Regra pura: os 4 níveis, fronteiras (75%, 30 mm/h, alerta, crítico), entradas inválidas, prioridade |
| `tests/test_corregos.py` | CRUD de córregos, camelCase, 404, 422 de limites, status, sensores (404/409) |
| `tests/test_leituras.py` | Leitura normal sem alerta; **leitura crítica cria alerta e retorna prioritários**; 404/422; encerrar alerta |
| `tests/test_moradores.py` | Prioridade automática, prioritários por córrego, validação 422 (telefone/enum), 404, update/delete |

---

## Endpoints

Base: `/api` · JSON em camelCase.

| Método | Rota | Descrição | Respostas |
|---|---|---|---|
| GET | `/api/corregos` | Lista córregos | 200 |
| POST | `/api/corregos` | Cadastra córrego | 201, 422 |
| GET | `/api/corregos/{id}` | Detalha córrego | 200, 404 |
| PUT | `/api/corregos/{id}` | Atualiza córrego (parcial) | 200, 404, 422 |
| DELETE | `/api/corregos/{id}` | Remove córrego (cascata) | 204, 404 |
| GET | `/api/corregos/{id}/status` | Último nível, chuva, nivelRisco, última leitura | 200, 404 |
| GET | `/api/sensores?corregoId=` | Lista sensores | 200 |
| POST | `/api/sensores` | Cadastra sensor ESP32 | 201, 404, 409, 422 |
| GET | `/api/sensores/{id}` | Detalha sensor | 200, 404 |
| POST | `/api/leituras` | Registra leitura → leitura + nivelRisco + alerta + moradoresPrioritarios | 201, 404, 422 |
| GET | `/api/leituras?corregoId=&limite=` | Lista leituras recentes | 200, 404 |
| GET | `/api/moradores?corregoId=` | Lista moradores | 200 |
| POST | `/api/moradores` | Cadastra morador | 201, 404, 422 |
| GET | `/api/moradores/prioritarios?corregoId=` | Lista moradores prioritários | 200, 404 |
| GET | `/api/moradores/{id}` | Detalha morador | 200, 404 |
| PUT | `/api/moradores/{id}` | Atualiza morador (parcial) | 200, 404, 422 |
| DELETE | `/api/moradores/{id}` | Remove morador | 204, 404 |
| GET | `/api/alertas?ativos=true&corregoId=` | Lista alertas | 200 |
| PATCH | `/api/alertas/{id}/encerrar` | Encerra alerta | 200, 404, 409 |
| GET | `/` | Health check | 200 |

Erros seguem o formato `{"detail": "mensagem"}` (404/409) ou o padrão de validação do FastAPI (422).

### Exemplos (curl)

```bash
# Status do Córrego Ponte Baixa (seed)
curl http://127.0.0.1:8000/api/corregos/1/status

# ESP32 envia leitura CRÍTICA (nível 190 cm >= 180 cm)
curl -X POST http://127.0.0.1:8000/api/leituras \
  -H "Content-Type: application/json" \
  -d '{"sensorId": 1, "nivelAguaCm": 190, "chuvaMmHora": 55}'
```

Resposta (resumida):
```json
{
  "leitura": { "id": 6, "sensorId": 1, "nivelAguaCm": 190.0, "chuvaMmHora": 55.0, "registradaEm": "..." },
  "nivelRisco": "CRITICO",
  "alerta": {
    "id": 2, "corregoId": 1, "nivelRisco": "CRITICO", "nivelAguaCm": 190.0, "ativo": true,
    "mensagem": "RISCO CRÍTICO: Córrego Ponte Baixa atingiu 190 cm e pode transbordar a qualquer momento. ...",
    "criadoEm": "..."
  },
  "moradoresPrioritarios": [
    { "id": 1, "nome": "Dona Benedita (fictícia)", "telefone": "(11) 90000-0001", "endereco": "Rua Fictícia das Flores, 10", "tipoNecessidade": "IDOSO" },
    { "id": 2, "nome": "Seu Joaquim (fictício)", "telefone": "(11) 90000-0002", "endereco": "Rua Fictícia das Flores, 22", "tipoNecessidade": "CADEIRANTE" }
  ]
}
```

```bash
# Cadastrar morador (vira prioritário por ser cadeirante)
curl -X POST http://127.0.0.1:8000/api/moradores \
  -H "Content-Type: application/json" \
  -d '{"nome":"Morador Fictício","telefone":"(11) 90000-0099","endereco":"Rua Exemplo, 50","corregoId":2,"tipoNecessidade":"CADEIRANTE"}'

# Moradores prioritários do córrego 1
curl "http://127.0.0.1:8000/api/moradores/prioritarios?corregoId=1"

# Alertas ativos do córrego 1 e encerramento
curl "http://127.0.0.1:8000/api/alertas?ativos=true&corregoId=1"
curl -X PATCH http://127.0.0.1:8000/api/alertas/1/encerrar

# Últimas 10 leituras do córrego 1
curl "http://127.0.0.1:8000/api/leituras?corregoId=1&limite=10"
```

---

## Documentação automática (Swagger)

O FastAPI gera a especificação **OpenAPI 3** automaticamente a partir dos routers e schemas
Pydantic: cada endpoint tem `summary`, `description`, tag por recurso, `response_model`, status
codes e respostas de erro documentadas; os schemas trazem exemplos (`examples`) e validações
(mínimos, máximos, regex de telefone, enums).

- Swagger UI: `/docs` · ReDoc: `/redoc` · JSON: `/openapi.json`

---

## Evidências

> Prints da aplicação em execução (salvar em `docs/evidencias/`).

| Evidência | Arquivo |
|---|---|
| Swagger UI com todos os endpoints | ![Swagger](docs/evidencias/swagger.png) |
| `POST /api/leituras` crítico gerando alerta + prioritários | ![Leitura crítica](docs/evidencias/leitura-critica.png) |
| `GET /api/corregos/1/status` | ![Status](docs/evidencias/status-corrego.png) |
| `alembic upgrade head` executado | ![Migrações](docs/evidencias/migracoes.png) |
| Tabelas e dados no banco (DB Browser for SQLite / psql) | ![Banco](docs/evidencias/banco.png) |
| `pytest` com todos os testes passando | ![Testes](docs/evidencias/testes.png) |

---

## Uso de IA

A IA foi usada como copiloto; os principais prompts e o que foi validado pela equipe estão em
[`prompts.md`](prompts.md).

## Tecnologias
Python 3.11+ · FastAPI · SQLAlchemy 2.x · Alembic · Pydantic v2 · SQLite / PostgreSQL · pytest · Uvicorn
