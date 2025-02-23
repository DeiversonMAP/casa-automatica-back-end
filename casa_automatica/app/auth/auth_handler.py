from datetime import datetime, timedelta
from typing import Union
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Chave secreta do JWT
ALGORITHM = "HS256"  # Algoritmo de criptografia do JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Tempo de expiração do token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ✅ Gerar hash da senha
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ✅ Verificar se a senha digitada corresponde ao hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ✅ Criar Token JWT
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ✅ Verificar Token JWT
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


# ✅ Dependência para proteger rotas
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if "sub" not in payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    return payload
