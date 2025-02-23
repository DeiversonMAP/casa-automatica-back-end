from fastapi import APIRouter, HTTPException, Depends
from app.auth.auth_handler import get_current_user
from app.database import db
from passlib.context import CryptContext
from app.models.schemas import UsuarioCreate, UsuarioResponse  # Importando os modelos

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/", response_model=UsuarioResponse)
async def criar_usuario(usuario: UsuarioCreate):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        try:
            # Verifica se o e-mail já está em uso
            email_existente = await connection.fetchrow(
                "SELECT id FROM usuarios WHERE email = $1", usuario.email
            )
            if email_existente:
                raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

            # Gerar hash da senha
            senha_hash = pwd_context.hash(usuario.senha)

            # Inserir no banco e retornar os dados do usuário
            novo_usuario = await connection.fetchrow(
                "INSERT INTO usuarios (nome, email, senha_hash) VALUES ($1, $2, $3) RETURNING id, nome, email",
                usuario.nome,
                usuario.email,
                senha_hash,
            )

            if not novo_usuario:
                raise HTTPException(status_code=500, detail="Erro ao criar usuário.")

            return UsuarioResponse(**novo_usuario)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


# ✅ Obter dados do usuário autenticado
@router.get("/me", response_model=UsuarioResponse)
async def obter_me(payload: str = Depends(get_current_user)):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        usuario = await connection.fetchrow(
            "SELECT id, nome, email FROM usuarios WHERE email = $1", payload.sub
        )
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return UsuarioResponse(**dict(usuario))


# ✅ Listar todos os usuários (Protegido)
@router.get("/", response_model=list[UsuarioResponse])
async def listar_usuarios(payload: str = Depends(get_current_user)):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        usuarios = await connection.fetch("SELECT id, nome, email FROM usuarios")
        return [UsuarioResponse(**dict(usuario)) for usuario in usuarios]


@router.get("/email/{email}", response_model=UsuarioResponse)
async def obter_usuario_por_email(email: str):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        usuario = await connection.fetchrow(
            "SELECT id, nome, email FROM usuarios WHERE email = $1", email
        )

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        return UsuarioResponse(**usuario)


@router.delete("/{usuario_id}")
async def deletar_usuario(usuario_id: int):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        usuario = await connection.fetchrow(
            "SELECT id FROM usuarios WHERE id = $1", usuario_id
        )
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")

        # Deleta dispositivos primeiro
        await connection.execute(
            "DELETE FROM dispositivos WHERE usuario_id = $1", usuario_id
        )

        # Depois, deleta o usuário
        await connection.execute("DELETE FROM usuarios WHERE id = $1", usuario_id)

        return {"mensagem": "Usuário e dispositivos deletados com sucesso."}
