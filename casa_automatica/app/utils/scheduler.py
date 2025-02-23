import asyncio
import asyncpg
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import db


# ✅ Função para verificar e executar rotinas agendadas
async def verificar_rotinas_agendadas():
    """Verifica e executa rotinas agendadas."""
    throw("🕒 Verificando rotinas agendadas (função)...")
    conn = await db.get_connection()
    async with conn.acquire() as connection:
        try:
            rotinas = await connection.fetch(
                """
                SELECT id, nome, horario FROM rotinas
                WHERE tipo_execucao = 'agendada'
                AND horario <= NOW()
                """
            )

            if not rotinas:
                print("🔍 Nenhuma rotina agendada para executar no momento.")
                return

            for rotina in rotinas:
                print(f"🔄 Executando rotina: {rotina['nome']}")

                # Buscar os dispositivos associados à rotina
                dispositivos = await connection.fetch(
                    """
                    SELECT d.id, d.nome, d.status
                    FROM dispositivos d
                    JOIN rotina_dispositivos rd ON d.id = rd.dispositivo_id
                    WHERE rd.rotina_id = $1
                    """,
                    rotina["id"],
                )

                novo_status = True if rotina["acao"] == "ligar" else False

                # Atualizar status dos dispositivos
                for dispositivo in dispositivos:
                    await connection.execute(
                        "UPDATE dispositivos SET status = $1 WHERE id = $2",
                        novo_status,
                        dispositivo["id"],
                    )

                print(f"✅ Rotina '{rotina['nome']}' executada com sucesso!")
        except asyncpg.exceptions.ConnectionDoesNotExistError:
            print("⚠️ Conexão com o banco de dados foi perdida. Tentando reconectar...")
        except Exception as e:
            print(f"❌ Erro ao verificar rotinas agendadas: {e}")


def agendar_verificacao():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    print("🕒 Verificando rotinas agendadas...")
    loop.create_task(verificar_rotinas_agendadas())


# ✅ Agendador para rodar a cada minuto
def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(agendar_verificacao, "interval", minutes=1)
    scheduler.start()
    print("⏳ Agendador iniciado para verificar rotinas a cada 1 minuto.")
