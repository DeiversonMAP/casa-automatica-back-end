from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Union, List
from datetime import datetime


# ✅ Esquema para criação de usuário
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str


# ✅ Esquema para resposta ao listar usuários (evita expor a senha)
class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ✅ Esquema para criação de dispositivo
class DispositivoCreate(BaseModel):
    nome: str
    usuario_id: int


# ✅ Esquema para resposta ao listar dispositivos
class DispositivoResponse(BaseModel):
    id: int
    nome: str
    usuario_id: int
    status: Optional[Union[str, bool]] = "desligado"  # Aceita string e booleano

    @field_validator("status", mode="before")
    def convert_status(cls, v):
        if isinstance(v, bool):  # Converte booleano para string
            return "ligado" if v else "desligado"
        return v


# ✅ Schema para criar uma rotina
class RotinaCreate(BaseModel):
    nome: str
    dispositivos_ids: List[int]  # IDs dos dispositivos associados à rotina
    tipo: str  # "imediato" ou "agendado"
    horario: Optional[datetime] = None  # Necessário se for "agendado"


# ✅ Schema para exibir uma rotina
class RotinaResponse(BaseModel):
    id: int
    nome: str
    tipo: str
    horario: Optional[datetime]
    dispositivos_ids: List[int]


# ✅ Schema para mensagens de resposta genéricas
class MensagemResponse(BaseModel):
    mensagem: str
    dispositivos_afetados: List[str]
