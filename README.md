# VetCare: clínica veterinária em microsserviços

Projeto da disciplina **Sistemas Distribuídos**, do Centro Universitário SATC (Prof.ª Dra. Kajiana Nuernberg Sartor Vidotto).

Back-end de uma clínica veterinária dividido em **quatro microsserviços** independentes. Ele foi feito com Python, Flask, Flask-SQLAlchemy (SQLite), API REST com JSON e `requests`, no mesmo padrão da atividade guiada (Contas e Movimentos).

**Equipe:** Henrique Lucio Coral, Cauã Savi e José Victor
**Turma:** Arquitetura de Software, Sexta (Noturno)

### Links da entrega

- **GitHub:** https://github.com/henriquecoral06/vetcare-microsservicos
- **Render (serviços publicados):**
  - Tutores: https://vetcare-tutores.onrender.com/api/health
  - Pets: https://vetcare-pets.onrender.com/api/health
  - Veterinários: https://vetcare-veterinarios.onrender.com/api/health
  - Consultas: https://vetcare-consultas.onrender.com/api/health
- **Coleção do Thunder Client:** `thunder-client-colecao.json`, com uma pasta "Integrações".

No plano gratuito do Render, os serviços hibernam depois de 15 minutos sem uso. A primeira chamada pode levar cerca de 1 minuto para responder.

### Participação da equipe

O projeto foi desenvolvido em conjunto e presencialmente pelos três integrantes. Henrique escreveu o código enquanto o grupo discutia e decidia junto.

| Integrante | Participação |
|---|---|
| **Henrique Lucio Coral** | Implementação dos serviços, integrações e publicação no Render. |
| **Cauã Savi** | Definição do domínio e das integrações, revisão do serviço de Tutores e testes no Thunder Client. |
| **José Victor** | Definição do domínio e das integrações, revisão do serviço de Pets e testes no Thunder Client. |

---

## 1. Documento de requisitos

### 1.1 Propósito do sistema

Organizar o atendimento de uma clínica veterinária. O sistema guarda os **tutores** (donos), os **pets**, os **veterinários** e as **consultas**. Quando uma consulta é agendada, o sistema confere se o pet e o veterinário estão ativos. Depois ele lança o valor da consulta no saldo devedor do tutor. Se a consulta for cancelada, o valor é estornado.

### 1.2 Usuários

| Usuário | O que faz no sistema |
|---|---|
| **Recepcionista** | Cadastra tutores e pets, agenda, remarca e cancela consultas. |
| **Veterinário** | Consulta a agenda e os dados do pet e do tutor. |
| **Gerente da clínica** | Cadastra veterinários e o valor da consulta e acompanha o saldo devedor dos tutores. |

### 1.3 Requisitos funcionais

| Código | Requisito | Serviço |
|---|---|---|
| RF01 | Cadastrar, listar, buscar, editar e inativar **tutores** (nome, CPF único, telefone, e-mail). | Tutores |
| RF02 | Manter o **saldo devedor** de cada tutor, permitindo lançar e estornar valores. | Tutores |
| RF03 | Cadastrar, listar, buscar, editar e inativar **veterinários** (nome, CRMV único, especialidade, valor da consulta). | Veterinários |
| RF04 | Cadastrar, listar (inclusive por tutor), buscar, editar e inativar **pets** (nome, espécie, raça, idade, tutor). | Pets |
| RF05 | Ao cadastrar um pet, validar se o tutor existe e está ativo. | Pets → Tutores |
| RF06 | Ao consultar um pet, exibir também os dados do seu tutor. | Pets → Tutores |
| RF07 | Agendar **consultas** (pet, veterinário, data/hora, motivo), validando se o pet e o veterinário existem e estão ativos. | Consultas → Pets / Veterinários |
| RF08 | Usar o valor da consulta definido no cadastro do veterinário. | Consultas → Veterinários |
| RF09 | Ao agendar uma consulta, lançar o valor no saldo devedor do tutor do pet. | Consultas → Tutores |
| RF10 | Listar (inclusive por pet), buscar e remarcar consultas (data/hora e motivo). | Consultas |
| RF11 | Cancelar uma consulta, estornando o valor do saldo devedor do tutor. | Consultas → Tutores |
| RF12 | Se outro serviço estiver fora do ar ou recusar o pedido, devolver um erro claro e desfazer o que já foi gravado (compensação). | Todos |

---

## 2. Descritivo técnico

### 2.1 Os microsserviços

| Serviço | Pasta | Porta | Banco | Função | Chama quem |
|---|---|---|---|---|---|
| **Tutores** | `servico_tutores/` | 5001 | `tutores.db` | Dados dos tutores e o **saldo devedor** de cada um. | Ninguém |
| **Pets** | `servico_pets/` | 5002 | `pets.db` | Dados dos pets. Guarda só o `tutor_id`. | Tutores |
| **Veterinários** | `servico_veterinarios/` | 5003 | `veterinarios.db` | Dados dos veterinários e o **valor da consulta**. | Ninguém |
| **Consultas** | `servico_consultas/` | 5004 | `consultas.db` | Agenda de consultas. Guarda só `pet_id`, `veterinario_id` e `tutor_id`. | Pets, Veterinários e Tutores |

Cada serviço tem a mesma estrutura da atividade guiada:

```
servico_x/
  app.py            cria o Flask, o banco, o /api/health e os logs no terminal
  models.py         a "tabela" do serviço (Flask-SQLAlchemy + SQLite)
  regras.py         as regras de negócio
  rotas.py          a API REST (JSON)
  erros.py          RegraDeNegocioError -> resposta HTTP 400
  <nome>_helper.py  o "telefone" para outro serviço (requests, timeout de 5 s)
  requirements.txt  usado pelo Render
```

Regras seguidas em todas as integrações:

- Um serviço **nunca** acessa o banco do outro. A comunicação é só por requisição HTTP.
- Cada serviço guarda **apenas o id** do registro do outro serviço, **sem ForeignKey entre bancos**.
- Os endereços dos outros serviços ficam em **variáveis de ambiente** (`TUTORES_URL`, `PETS_URL`, `VETERINARIOS_URL`). O padrão é `http://127.0.0.1:<porta>`.
- Todo helper usa **timeout de 5 segundos**. Se o outro serviço estiver fora do ar ou demorar demais, o cliente recebe um erro claro, por exemplo `"O serviço de Tutores está indisponível. Tente mais tarde."`. O programa não quebra.

### 2.2 As integrações

| # | Tipo | Quem chama | Quem responde | Rota usada | O que pergunta ou pede | Se o outro estiver fora do ar |
|---|---|---|---|---|---|---|
| **1** | **Busca (GET)** | Pets | Tutores | `GET /api/tutores/<id>` | Ao consultar um pet (`GET /api/pets/<id>`), traz os dados do tutor. Também valida o tutor ao cadastrar o pet. | A consulta do pet continua funcionando, com `"tutor": null` e um `"aviso"`. O cadastro do pet é recusado com erro 400 claro. |
| **2** | **Busca (GET)** | Consultas | Veterinários | `GET /api/veterinarios/<id>` | Ao agendar, confere se o veterinário existe e está ativo e pega o `valor_consulta`. | A consulta não é gravada. O cliente recebe 400 com "O serviço de Veterinários está indisponível". |
| **3** | **Alteração (POST)** | Consultas | Tutores | `POST /api/tutores/<id>/debitos` `{"tipo":"lancar","valor":150}` | Ao agendar, lança o valor da consulta no saldo devedor do tutor. | **Compensação:** a consulta já gravada é apagada e o cliente recebe 400 com a mensagem do erro. |

Integrações a mais, que usam o mesmo padrão:

- **Consultas → Pets** (`GET /api/pets/<id>/resumo`): ao agendar, confere se o pet existe e está ativo e descobre quem é o tutor.
- **Consultas → Tutores** (`POST /api/tutores/<id>/debitos` com `"tipo":"estornar"`): ao cancelar uma consulta, estorna o valor. O status só muda para `cancelada` se o estorno der certo.

### 2.3 Fluxo do agendamento de uma consulta

```
Thunder Client
   │  POST /api/consultas {"pet_id":1,"veterinario_id":1,"data_hora":"...","motivo":"..."}
   ▼
CONSULTAS (5004)
   │ passo 1 ── GET /api/pets/1/resumo ───────────────►  PETS (5002)
   │         ◄── 200 {"ativo":true,"tutor_id":1}
   │ passo 2 ── GET /api/veterinarios/1 ──────────────►  VETERINARIOS (5003)
   │         ◄── 200 {"ativo":true,"valor_consulta":150}
   │ passo 3 ── grava a consulta no consultas.db
   │ passo 4 ── POST /api/tutores/1/debitos ──────────►  TUTORES (5001)
   │            {"tipo":"lancar","valor":150}             saldo_devedor += 150
   │         ◄── 200   (se falhar: apaga a consulta = compensação)
   ▼
Thunder Client ◄── 201 {"id":1,"status":"agendada","valor":150.0,...}
```

### 2.4 Logs padronizados

Assim como na atividade guiada, cada serviço mostra no terminal (e na aba **Logs** do Render) o que recebeu e com quem conversou:

```
[CONSULTAS] passo 4: peço ao TUTORES para lançar 150.00 no saldo devedor do tutor 2
[CONSULTAS]   >>> ligando para TUTORES: POST /api/tutores/2/debitos
[CONSULTAS]   <<< TUTORES não atendeu (fora do ar?)
[CONSULTAS] deu errado: apago a consulta gravada (compensação)
[CONSULTAS] regra violada: O serviço de Tutores está indisponível. Tente mais tarde.
[CONSULTAS] recebi POST /api/consultas -> respondi 400
```

---

## 3. Rotas da API

Todos os serviços têm `GET /api/health`, que responde `{"status": "no ar", "servico": "..."}`.

| Serviço | Método e rota | Descrição |
|---|---|---|
| Tutores | `POST /api/tutores` | Cadastrar `{"nome","cpf","telefone","email"}` |
| | `GET /api/tutores` / `GET /api/tutores/<id>` | Listar / buscar |
| | `PUT /api/tutores/<id>` | Editar `{"nome","telefone","email"}` |
| | `DELETE /api/tutores/<id>` | Inativar |
| | `POST /api/tutores/<id>/debitos` | Lançar ou estornar `{"tipo":"lancar"\|"estornar","valor"}` (usado por Consultas) |
| Pets | `POST /api/pets` | Cadastrar `{"nome","especie","raca","idade","tutor_id"}` (valida o tutor) |
| | `GET /api/pets` (`?tutor_id=`) | Listar |
| | `GET /api/pets/<id>` | Buscar **com os dados do tutor** (Integração 1) |
| | `GET /api/pets/<id>/resumo` | Buscar sem chamar ninguém (usado por Consultas) |
| | `PUT /api/pets/<id>` / `DELETE /api/pets/<id>` | Editar / inativar |
| Veterinários | `POST /api/veterinarios` | Cadastrar `{"nome","crmv","especialidade","valor_consulta"}` |
| | `GET /api/veterinarios` / `GET /api/veterinarios/<id>` | Listar / buscar (Integração 2) |
| | `PUT /api/veterinarios/<id>` / `DELETE /api/veterinarios/<id>` | Editar / inativar |
| Consultas | `POST /api/consultas` | Agendar `{"pet_id","veterinario_id","data_hora":"2026-11-25T14:30","motivo"}` (Integrações 2 e 3) |
| | `GET /api/consultas` (`?pet_id=`) / `GET /api/consultas/<id>` | Listar / buscar |
| | `PUT /api/consultas/<id>` | Remarcar `{"data_hora","motivo"}` |
| | `PATCH /api/consultas/<id>/cancelar` | Cancelar e estornar no Tutores |

Espécies aceitas: `cachorro`, `gato`, `ave`, `roedor`, `outro`.

**Dados de exemplo:** quando o banco está vazio (por exemplo, depois de um reinício no Render), cada serviço cria um registro inicial. São eles: a tutora **Ana Souza** (id 1), o pet **Thor** (id 1, tutor 1) e o **Dr. Carlos Lima** (id 1, consulta de R$ 150,00).

---

## 4. Como rodar no computador

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / Mac
pip install -r requirements.txt
```

Abra **quatro terminais** no VS Code, um para cada serviço:

```bash
cd servico_tutores        && python app.py   # porta 5001
cd servico_pets           && python app.py   # porta 5002
cd servico_veterinarios   && python app.py   # porta 5003
cd servico_consultas      && python app.py   # porta 5004
```

No Windows, se `python` não for reconhecido, use `py`.

## 5. Demonstração (Thunder Client)

Importe o arquivo `thunder-client-colecao.json` em **Collections → ⋯ → Import**. A coleção tem uma pasta para cada serviço (CRUD) e a pasta **Integrações**, com as requisições na ordem da demonstração:

1. **Integração 1 (GET):** buscar o pet 1 e ver os dados do tutor.
2. **Integração 2 e 3:** agendar uma consulta. Consultas busca o veterinário e lança o débito no Tutores.
3. Conferir o saldo devedor do tutor (subiu R$ 150,00).
4. Cancelar a consulta e conferir o estorno.
5. **Falhas:** desligar o Tutores (Ctrl + C) e repetir o agendamento. A consulta é desfeita (compensação) e a mensagem de erro é clara.

## 6. Publicação no Render

Cada pasta de serviço vira um **Web Service** no Render:

| Campo | Valor |
|---|---|
| Root Directory | `servico_tutores`, `servico_pets`, `servico_veterinarios` ou `servico_consultas` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Instance Type | Free |

Variáveis de ambiente (**Environment**), com a URL pública e **sem barra no final**:

| Serviço | Key | Value |
|---|---|---|
| Pets | `TUTORES_URL` | `https://<servico-tutores>.onrender.com` |
| Consultas | `TUTORES_URL` | `https://<servico-tutores>.onrender.com` |
| Consultas | `PETS_URL` | `https://<servico-pets>.onrender.com` |
| Consultas | `VETERINARIOS_URL` | `https://<servico-veterinarios>.onrender.com` |

**Endereços publicados:**

| Serviço | Endereço público | Health |
|---|---|---|
| Tutores | https://vetcare-tutores.onrender.com | [/api/health](https://vetcare-tutores.onrender.com/api/health) |
| Pets | https://vetcare-pets.onrender.com | [/api/health](https://vetcare-pets.onrender.com/api/health) |
| Veterinários | https://vetcare-veterinarios.onrender.com | [/api/health](https://vetcare-veterinarios.onrender.com/api/health) |
| Consultas | https://vetcare-consultas.onrender.com | [/api/health](https://vetcare-consultas.onrender.com/api/health) |

Para testar a versão publicada no Thunder Client, troque `http://127.0.0.1:500X` pelo endereço do serviço correspondente. Exemplos:

- Integração 1: `GET https://vetcare-pets.onrender.com/api/pets/1`
- Integrações 2 e 3: `POST https://vetcare-consultas.onrender.com/api/consultas`
- Conferir o débito: `GET https://vetcare-tutores.onrender.com/api/tutores/1`

Antes de demonstrar, chame `/api/health` de cada serviço para "acordar" os quatro. No plano gratuito eles hibernam depois de 15 minutos sem acesso.
