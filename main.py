from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.database import db
from app.routes import usuarios, dispositivos, rotinas, auth
from app.utils.scheduler import iniciar_scheduler
from contextlib import asynccontextmanager


# Conectar ao banco e iniciar o scheduler ao iniciar a API
@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Altere para ["http://127.0.0.1:5500"] se quiser mais segurança
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os headers
)

# ✅ Registrar os roteadores
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(usuarios.router, prefix="/user", tags=["Usuários"])
app.include_router(dispositivos.router, prefix="/device", tags=["Dispositivos"])
app.include_router(rotinas.router, prefix="/routine", tags=["Rotinas"])

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ✅ Health Check da API
@app.get("/")
async def health_check():
    return {"mensagem": "API está rodando!"}


# ✅ Health Check do Banco de Dados
@app.get("/health/db")
async def health_check_db():
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        try:
            await connection.fetchval("SELECT 1")  # Testa a conexão com o banco
            return {"status": "OK", "mensagem": "Banco de dados conectado!"}
        except Exception as e:
            raise HTTPException(
                status_code=503, detail=f"Erro ao conectar ao banco: {str(e)}"
            )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
