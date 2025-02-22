from fastapi import FastAPI, Depends
from app.database import db
from app.routes import usuarios, dispositivos, rotinas, auth  # Importamos os roteadores

app = FastAPI()

# Conectar ao banco ao iniciar a API
app.add_event_handler("startup", db.connect)
app.add_event_handler("shutdown", db.disconnect)

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
