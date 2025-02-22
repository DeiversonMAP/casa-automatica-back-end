# Comandos importantes

#### Instalar requirements:
```sh
pip install -r requirements.txt
```

#### Ativar ambiente virtual:
```sh 
venv\Scripts\activate
```  

#### Rodar o python:
```sh 
uvicorn app.main:app --reload
```  

##### Acessar o banco:

```sh
psql -h gondola.proxy.rlwy.net -U postgres -p 26737 -d railway
PASSWORD xKEcAOlUNzQbWAGZIAgQkroZOhvxQYkF
```



# 📌 Rotas do Sistema

## **Usuários (`routes/usuarios.py`)**
| Método  | Rota                  | Protegida? | Descrição |
|---------|------------------------|------------|-----------|
| `POST`  | `/user/`               | ❌         | Cria um novo usuário. |
| `GET`   | `/user/`               | ✅         | Lista todos os usuários. |
| `GET`   | `/user/me`             | ✅         | Retorna os dados do usuário autenticado. |
| `GET`   | `/user/email/{email}`  | ✅         | Obtém um usuário pelo e-mail. |
| `DELETE`| `/user/{usuario_id}`   | ✅         | Deleta um usuário e todos os dispositivos associados. |

## **Dispositivos (`routes/dispositivos.py`)**
| Método  | Rota                  | Protegida? | Descrição |
|---------|------------------------|------------|-----------|
| `POST`  | `/device/`             | ✅         | Cria um novo dispositivo. |
| `GET`   | `/device/`             | ✅         | Lista todos os dispositivos. |
| `GET`   | `/device/{usuario_id}` | ✅         | Lista dispositivos de um usuário específico. |
| `DELETE`| `/device/{dispositivo_id}` | ✅   | Deleta um dispositivo pelo ID. |

## **Autenticação (`routes/auth.py`)**
| Método  | Rota        | Protegida? | Descrição |
|---------|------------|------------|-----------|
| `POST`  | `/auth/login` | ❌      | Autentica o usuário e retorna um token JWT. |
| `GET`   | `/auth/me`    | ✅      | Retorna os dados do usuário autenticado. |

## **Health Checks**
| Método  | Rota         | Protegida? | Descrição |
|---------|-------------|------------|-----------|
| `GET`   | `/`         | ❌         | Verifica se a API está rodando. |
| `GET`   | `/health/db` | ❌        | Verifica a conexão com o banco de dados. |


---
## Tabelas do Bando de Dados PostgreSQL:
Foi utilizado https://railway.com/ para deploy do banco de dados

```sql
-- Criar a tabela de usuários
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar a tabela de dispositivos
CREATE TABLE dispositivos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    status BOOLEAN DEFAULT FALSE,
    usuario_id INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rotinas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) CHECK (tipo IN ('imediata', 'agendada')) NOT NULL,
    horario TIMESTAMP NULL,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rotina_dispositivos (
    id SERIAL PRIMARY KEY,
    rotina_id INTEGER NOT NULL,
    dispositivo_id INTEGER NOT NULL,
    acao VARCHAR(50) CHECK (acao IN ('ligar', 'desligar')) NOT NULL,
    FOREIGN KEY (rotina_id) REFERENCES rotinas(id) ON DELETE CASCADE,
    FOREIGN KEY (dispositivo_id) REFERENCES dispositivos(id) ON DELETE CASCADE
);

```










---
