# Comandos importantes

#### Ativar ambiente virtual:
```sh 
venv\Scripts\activate
```  

#### Instalar requirements:
```sh
pip install -r requirements.txt
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