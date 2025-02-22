from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.models.schemas import (
    DispositivoCreate,
    DispositivoResponse,
)  # Importando os modelos
from app.auth.auth_handler import get_current_user


router = APIRouter()


# @router.get("/", dependencies=[Depends(get_current_user)])
# async def listar_dispositivos():
#     return {"mensagem": "Esta é uma rota protegida!"}


@router.post("/", response_model=DispositivoResponse)
async def criar_dispositivo(
    dispositivo: DispositivoCreate, user=Depends(get_current_user)
):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        try:
            # Verifica se o usuário existe
            usuario = await connection.fetchrow(
                "SELECT id FROM usuarios WHERE id = $1", dispositivo.usuario_id
            )
            if not usuario:
                raise HTTPException(status_code=400, detail="Usuário não encontrado.")

            # Inserir o dispositivo no banco
            novo_dispositivo = await connection.fetchrow(
                "INSERT INTO dispositivos (nome, usuario_id) VALUES ($1, $2) RETURNING id, nome, usuario_id",
                dispositivo.nome,
                dispositivo.usuario_id,
            )

            if not novo_dispositivo:
                raise HTTPException(
                    status_code=500, detail="Erro ao criar dispositivo."
                )

            return DispositivoResponse(**novo_dispositivo)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


# ✅ Listar dispositivos de um usuário
@router.get("/{usuario_id}")
async def listar_dispositivos(usuario_id: int, user=Depends(get_current_user)):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        dispositivos = await connection.fetch(
            "SELECT id, nome, status FROM dispositivos WHERE usuario_id = $1",
            usuario_id,
        )
        if not dispositivos:
            raise HTTPException(
                status_code=404,
                detail="Nenhum dispositivo encontrado para este usuário.",
            )
        return {"dispositivos": [dict(dispositivo) for dispositivo in dispositivos]}


@router.get("/", response_model=list[DispositivoResponse])
async def listar_todos_dispositivos(user=Depends(get_current_user)):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        dispositivos = await connection.fetch(
            "SELECT id, nome, status, usuario_id FROM dispositivos ORDER BY id ASC"
        )
        return [
            DispositivoResponse(**dict(dispositivo)) for dispositivo in dispositivos
        ]


@router.delete("/{dispositivo_id}")
async def deletar_dispositivo(dispositivo_id: int, user=Depends(get_current_user)):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        dispositivo = await connection.fetchrow(
            "SELECT id FROM dispositivos WHERE id = $1", dispositivo_id
        )
        if not dispositivo:
            raise HTTPException(status_code=404, detail="Dispositivo não encontrado.")

        await connection.execute(
            "DELETE FROM dispositivos WHERE id = $1", dispositivo_id
        )

        return {"mensagem": "Dispositivo deletado com sucesso."}
