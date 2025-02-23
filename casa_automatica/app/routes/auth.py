from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.models.schemas import LoginRequest, TokenResponse
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.auth.auth_handler import get_current_user, get_token_data
import jwt
import os
from dotenv import load_dotenv
import asyncpg
from app.database import db
from fastapi.security import OAuth2PasswordBearer


load_dotenv()

router = APIRouter()

# Configuração do hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Configuração do JWT
SECRET_KEY = os.getenv("SECRET_KEY", "chave_secreta")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Tempo de expiração do token


# Função para criar um token JWT
def criar_token_jwt(dados: dict, expira_em: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = dados.copy()
    expire = datetime.utcnow() + timedelta(minutes=expira_em)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Rota de login
@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        usuario = await connection.fetchrow(
            "SELECT id, email, senha_hash FROM usuarios WHERE email = $1", request.email
        )
        if not usuario:
            raise HTTPException(status_code=400, detail="E-mail ou senha incorretos.")

        if not pwd_context.verify(request.senha, usuario["senha_hash"]):
            raise HTTPException(status_code=400, detail="E-mail ou senha incorretos.")

        # Criar token JWT
        access_token = criar_token_jwt({"sub": usuario["email"], "id": usuario["id"]})

        return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),  # ✅ Obtém o token JWT correto
    conn: asyncpg.Connection = Depends(db.get_connection),
):
    try:
        # Revoga o token armazenando no banco com a data de expiração
        expira_em = datetime.utcnow() + timedelta(
            days=7
        )  # Pode ajustar o tempo de retenção
        await conn.execute(
            "INSERT INTO tokens_revogados (token, expira_em) VALUES ($1, $2)",
            token,
            expira_em,
        )
        return {"message": "Logout realizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer logout: {str(e)}")


# ✅ Obter detalhes do usuário autenticado
@router.get("/me")
async def obter_usuario_autenticado(usuario_email: str = Depends(get_current_user)):
    return {"email": usuario_email, "mensagem": "Usuário autenticado com sucesso!"}
