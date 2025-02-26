# Comandos importantes


### Para iniciar o sistema rode os seguintes comandos:
#### Criar ambiente virtual
```sh
python -m venv venv
```

#### Ativar ambiente virtual:
```sh 
venv\Scripts\activate
```  

#### Instalar requirements:
```sh
pip install -r requirements.txt
```

#### Rodar os testes de unidade:

```sh
pytest tests/

```

#### Rodar o python:
```sh 
uvicorn main:app --reload
```  

---


# 📌 Rotas do Sistema

## 🛠️ Autenticação (`/auth`)
- **POST** `/auth/login` → Realiza login com e-mail e senha, retorna token JWT.  
- **GET** `/auth/me` → Retorna informações do usuário autenticado.  

## 👤 Usuários (`/user`)
- **GET** `/user/` → Lista todos os usuários.  
- **POST** `/user/` → Cria um novo usuário.  
- **GET** `/user/me` → Retorna os dados do usuário autenticado.
- **GET** `/user/{email}` → Obtém um usuário pelo e-mail.  
- **DELETE** `/user/{usuario_id}` → Deleta um usuário e todos os seus dispositivos.  

## 📱 Dispositivos (`/device`)
- **POST** `/device/` → Cria um novo dispositivo.  
- **GET** `/device/` → Lista todos os dispositivos.  
- **GET** `/device/{usuario_id}` → Lista dispositivos de um usuário.  
- **DELETE** `/device/{dispositivo_id}` → Deleta um dispositivo.  

## 🔄 Rotinas (`/routine`)
- **GET** `/routine/` → Lista todas as rotinas.  
- **POST** `/routine/` → Cria uma nova rotina.  
- **GET** `/routine/{rotina_id}` → Obtém rotina pelo id.  
- **PUT** `/routine/{rotina_id}` → Edita rotina.
- **DELETE** `/routine/{rotina_id}` → Deleta uma rotina.  
- **GET** `/routine/user/{usuario_id}` → Lista todas as rotinas de um usuário.  
- **GET** `/routine/device/{dispositivo_id}` → Lista todas as rotinas associadas a um dispositivo.  
- **POST** `/routine/{rotina_id}/run` → Executa uma rotina imediatamente, atualizando o status dos dispositivos.  

## 🩺 Health Check
- **GET** `/` → Verifica se a API está rodando.  
- **GET** `/health/db` → Verifica a conexão com o banco de dados.  

----
## Banco de Dados

#### Acessar o banco:
```sh
psql -h gondola.proxy.rlwy.net -U postgres -p 26737 -d railway
PASSWORD xKEcAOlUNzQbWAGZIAgQkroZOhvxQYkF
```
#### Criação das Tabelas
```sql
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dispositivos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    usuario_id INTEGER NOT NULL,
    status BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rotinas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) CHECK (tipo IN ('imediata', 'agendada')) NOT NULL,
    acao VARCHAR(10) NOT NULL CHECK (acao IN ('ativar', 'desativar')),
    horario TIMESTAMP NULL,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rotina_dispositivos (
    id SERIAL PRIMARY KEY,
    rotina_id INTEGER NOT NULL,
    dispositivo_id INTEGER NOT NULL,
    acao VARCHAR(10) NOT NULL,
    FOREIGN KEY (rotina_id) REFERENCES rotinas(id) ON DELETE CASCADE,
    FOREIGN KEY (dispositivo_id) REFERENCES dispositivos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tokens_revogados (token TEXT PRIMARY KEY, expira_em TIMESTAMP);

```


---
## Framework Web (API)
Para criar a API que vai gerenciar os dispositivos escolhemos:
#### ✅ FastAPI
- 🚀 Muito rápido e otimizado para alto desempenho.
- 🏗️ Baseado em Pydantic e Type Hints, garantindo segurança de tipos.
- 📄 Swagger automático (gera documentação interativa automaticamente).
- 🔥 Ideal para APIs modernas e comunicação com IoT.
---
## Autenticação e Segurança
O sistema precisa garantir que apenas usuários autorizados possam acessar e modificar dispositivos. Algumas opções:

#### ✅ Autenticação JWT (Token baseado em JSON Web Tokens)

- Ideal para sistemas distribuídos e APIs seguras.
- FastAPI tem suporte nativo via OAuth2 + JWT.
---


## Escolha do Banco de Dados
Como o sistema lida com dispositivos, usuários e automações, é importante escolher um banco adequado.

#### ✅ PostgreSQL (Banco Relacional - Melhor escolha se precisar de estrutura sólida)

- Ideal para dados estruturados (usuários, dispositivos, logs de eventos).
- Suporte a JSON e consultas avançadas.
- Escalável e seguro.

#### ✅ MongoDB (Banco NoSQL - Melhor para logs e dados flexíveis)

- Ideal para dados sem estrutura fixa (logs de sensores, eventos de dispositivos).
- Permite armazenar estados e históricos de maneira fácil.
- Recomendado para sistemas altamente dinâmicos.
---
## Testes e Monitoramento
Para garantir que o sistema funcione corretamente:

 ✅ Testes Automatizados (Pytest)

### Testes de Unidade:
Os testes verificam se as principais funcionalidades do sistema de automação residencial estão funcionando corretamente.

Tudo começa com `test_criar_usuario`, que tenta encontrar um usuário pelo e-mail. Se ele não existir (retorno `404`), o teste cria um novo usuário. Em seguida, `test_login` verifica se esse usuário consegue fazer login com as credenciais criadas, garantindo que o sistema retorna um token JWT válido. Esse token será essencial para as próximas requisições.

Com o usuário logado, `test_criar_dispositivo` entra em ação. Ele busca o ID do usuário e cadastra um dispositivo associado a ele, garantindo que a relação entre ambos esteja correta.

Depois, vem `test_criar_rotina`, que é um passo além na automação. Esse teste certifica que o usuário pode criar uma rotina, vinculando-a ao dispositivo registrado anteriormente. Antes de tudo, ele também verifica se todas as variáveis globais (usuário, dispositivo e token) foram corretamente definidas.

Por fim, `test_excluir_usuario` finaliza o processo garantindo que o usuário pode ser excluído junto com seus dispositivos. Ele busca o usuário pelo e-mail, obtém seu ID e envia uma requisição de remoção. Se tudo correr bem, o sistema retorna uma confirmação de que tanto o usuário quanto os dispositivos foram apagados.

Cada teste foi pensado para garantir que o fluxo do sistema aconteça sem falhas, desde o cadastro até a exclusão dos dados. Isso assegura que tudo está rodando como deveria e evita problemas futuros.

### Teste de Integração
Os testes de integração verificam a comunicação entre diferentes partes do sistema.

#### Teste: Ativar uma Rotina e Atualizar Status dos Dispositivos

**Objetivo:** Testar se, ao ativar uma rotina, os dispositivos associados são atualizados corretamente.

**Cenário:**

1. Criar uma rotina "Manhã" que ativa um dispositivo "Lâmpada".
2. Enviar uma requisição POST /rotinas/1/ativar.
3. Verificar se a lâmpada teve o status atualizado para TRUE no banco de dados.
4. O servidor deve retornar 200 OK e uma confirmação da ação.

### Teste de Sistema

Os testes de sistema verificam o comportamento completo do sistema sob diferentes cenários.

#### Teste: Execução Completa de uma Rotina Agendada

**Objetivo:** Testar se uma rotina agendada é corretamente executada no horário definido.

**Cenário:**

1. Criar uma rotina "Noite" para desligar todos os dispositivos às 22h.
2. Associar dispositivos à rotina com ações de "desativar".
3. Aguardar a execução do sistema até o horário programado.
4. Verificar se os dispositivos foram desligados corretamente.
5. O sistema deve registrar a execução da rotina.


---
