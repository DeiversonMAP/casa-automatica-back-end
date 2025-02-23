import asyncpg
import asyncio
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)
        await self.create_tables()  # Chama a criação de tabelas ao conectar

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def get_connection(self):
        if not self.pool:
            await self.connect()
        return self.pool

    async def create_tables(self):
        """Cria as tabelas se elas não existirem."""
        async with self.pool.acquire() as connection:
            await connection.execute(
                """
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        senha_hash TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS dispositivos (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        usuario_id INTEGER NOT NULL,
                        status BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS rotinas (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        tipo VARCHAR(50) CHECK (tipo IN ('imediata', 'agendada')) NOT NULL,
                        acao VARCHAR(10) NOT NULL CHECK (acao IN ('ativar', 'desativar')),
                        horario TIMESTAMP NULL,
                        usuario_id INTEGER NOT NULL,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS rotina_dispositivos (
                        id SERIAL PRIMARY KEY,
                        rotina_id INTEGER NOT NULL,
                        dispositivo_id INTEGER NOT NULL,
                        acao VARCHAR(10) NOT NULL,
                        FOREIGN KEY (rotina_id) REFERENCES rotinas(id) ON DELETE CASCADE,
                        FOREIGN KEY (dispositivo_id) REFERENCES dispositivos(id) ON DELETE CASCADE
                    );
                    
                    CREATE TABLE IF NOT EXISTS tokens_revogados (token TEXT PRIMARY KEY, expira_em TIMESTAMP);
            """
            )


db = Database()
