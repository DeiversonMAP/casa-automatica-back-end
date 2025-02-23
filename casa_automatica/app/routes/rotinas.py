from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.models.schemas import RotinaCreate, RotinaResponse, MensagemResponse
from app.auth.auth_handler import get_current_user
from typing import List

router = APIRouter()


# Criar uma rotina
@router.post("/", response_model=RotinaResponse)
async def criar_rotina(rotina: RotinaCreate, payload=Depends(get_current_user)):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        try:
            print(f"\n🚀 usuario_id: {payload}")
            nova_rotina = await connection.fetchrow(
                """
                INSERT INTO rotinas (nome, tipo, horario, acao, usuario_id)
                VALUES ($1, $2, $3, $4 , $5) RETURNING id, nome, tipo, horario, acao, usuario_id
                """,
                rotina.nome,
                rotina.tipo,
                rotina.horario,
                rotina.acao,
                payload["id"],
            )
            # Verifica se há dispositivos na rotina
            if rotina.dispositivos_ids:
                for dispositivo_id in rotina.dispositivos_ids:
                    await connection.execute(
                        """
                        INSERT INTO rotina_dispositivos (rotina_id, dispositivo_id , acao)
                        VALUES ($1, $2, $3)
                        """,
                        nova_rotina["id"],
                        dispositivo_id,
                        rotina.acao,
                    )

            return RotinaResponse(**nova_rotina)

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


# Listar todas as rotinas de um usuário
@router.get("/", response_model=list[RotinaResponse])
async def listar_rotinas(payload=Depends(get_current_user)):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        rotinas = await connection.fetch(
            "SELECT * FROM rotinas WHERE usuario_id = $1", payload["id"]
        )
        return [RotinaResponse(**dict(rotina)) for rotina in rotinas]


# Obter uma rotina pelo ID
@router.get("/{rotina_id}", response_model=RotinaResponse)
async def obter_rotina(rotina_id: int, payload=Depends(get_current_user)):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        rotina = await connection.fetchrow(
            "SELECT * FROM rotinas WHERE id = $1 AND usuario_id = $2",
            rotina_id,
            payload["id"],
        )
        if not rotina:
            raise HTTPException(status_code=404, detail="Rotina não encontrada")
        return RotinaResponse(**dict(rotina))


# Atualizar uma rotina
@router.put("/{rotina_id}", response_model=RotinaResponse)
async def atualizar_rotina(
    rotina_id: int, rotina: RotinaCreate, payload=Depends(get_current_user)
):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        updated_rotina = await connection.fetchrow(
            """
            UPDATE rotinas SET nome=$1, tipo=$2, horario=$3 , acao=$4
            WHERE id=$5 AND usuario_id=$6 RETURNING id, nome, tipo, horario, acao, usuario_id
            """,
            rotina.nome,
            rotina.tipo,
            rotina.horario,
            rotina.acao,
            rotina_id,
            payload["id"],
        )
        if not updated_rotina:
            raise HTTPException(status_code=404, detail="Rotina não encontrada")
        return RotinaResponse(**updated_rotina)


# ✅ Listar todas as rotinas de um usuário
@router.get("/user/{usuario_id}", response_model=List[RotinaResponse])
async def listar_rotinas_por_usuario(
    usuario_id: int, payload=Depends(get_current_user)
):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        rotinas = await connection.fetch(
            """
            SELECT r.id, r.nome, r.tipo, r.horario, r.acao,
                   ARRAY_AGG(rd.dispositivo_id) AS dispositivos_ids
            FROM rotinas r
            JOIN rotina_dispositivos rd ON r.id = rd.rotina_id
            WHERE r.usuario_id = $1
            GROUP BY r.id
            """,
            usuario_id,
        )

        if not rotinas:
            raise HTTPException(
                status_code=404, detail="Nenhuma rotina encontrada para este usuário."
            )

        return [RotinaResponse(**dict(rotina)) for rotina in rotinas]


# ✅ Listar todas as rotinas de um dispositivo
@router.get("/device/{dispositivo_id}", response_model=List[RotinaResponse])
async def listar_rotinas_por_dispositivo(
    dispositivo_id: int, payload=Depends(get_current_user)
):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        rotinas = await connection.fetch(
            """
            SELECT r.id, r.nome, r.tipo, r.horario, r.acao,
                   ARRAY_AGG(rd.dispositivo_id) AS dispositivos_ids
            FROM rotinas r
            JOIN rotina_dispositivos rd ON r.id = rd.rotina_id
            WHERE rd.dispositivo_id = $1
            GROUP BY r.id
            """,
            dispositivo_id,
        )

        if not rotinas:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma rotina encontrada para este dispositivo.",
            )

        return [RotinaResponse(**dict(rotina)) for rotina in rotinas]


# ✅ Executar uma rotina imediatamente
@router.post("/{rotina_id}/run", response_model=MensagemResponse)
async def executar_rotina_imediata(rotina_id: int, payload=Depends(get_current_user)):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        # Buscar a rotina
        rotina = await connection.fetchrow(
            "SELECT id, nome, tipo, acao FROM rotinas WHERE id = $1", rotina_id
        )

        if not rotina:
            raise HTTPException(status_code=404, detail="Rotina não encontrada.")

        if rotina["tipo"] != "imediata":
            raise HTTPException(
                status_code=400,
                detail="Essa rotina não pode ser executada imediatamente.",
            )

        # Buscar os dispositivos associados à rotina
        dispositivos = await connection.fetch(
            """
            SELECT d.id, d.nome, d.status
            FROM dispositivos d
            JOIN rotina_dispositivos rd ON d.id = rd.dispositivo_id
            WHERE rd.rotina_id = $1
            """,
            rotina_id,
        )

        if not dispositivos:
            raise HTTPException(
                status_code=400, detail="Nenhum dispositivo associado à rotina."
            )

        # Determinar a nova ação com base no tipo da rotina
        novo_status = True if rotina["acao"] == "ligar" else False

        # Atualizar status dos dispositivos
        for dispositivo in dispositivos:
            await connection.execute(
                "UPDATE dispositivos SET status = $1 WHERE id = $2",
                novo_status,
                dispositivo["id"],
            )

        dispositivos_afetados = [dispositivo["nome"] for dispositivo in dispositivos]

        return {
            "mensagem": f"Rotina '{rotina['nome']}' executada com sucesso.",
            "dispositivos_afetados": dispositivos_afetados,
        }


# Deletar uma rotina
@router.delete("/{rotina_id}")
async def deletar_rotina(rotina_id: int, payload=Depends(get_current_user)):
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        result = await connection.execute(
            "DELETE FROM rotinas WHERE id = $1 AND usuario_id = $2",
            rotina_id,
            payload["id"],
        )
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Rotina não encontrada")
        return {"mensagem": "Rotina deletada com sucesso"}
