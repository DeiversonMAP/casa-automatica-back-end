from fastapi.testclient import TestClient
from main import app
import pytest
from httpx import AsyncClient
import os

client = TestClient(app)

BASE_URL = os.getenv("BASE_URL")
TOKEN_GLOBAL = None  # Variável global para armazenar o token
USER_ID_GLOBAL = None
DEVICE_ID_GLOBAL = None
ROUTINE_ID_GLOBAL = None
EMAIL_TESTE = "joao@example.com"


@pytest.mark.asyncio
async def test_criar_usuario():
    async with AsyncClient(base_url=BASE_URL) as client:
        response_buscar = await client.get(f"/user/email/{EMAIL_TESTE}")
        assert response_buscar.status_code == 404

        response = await client.post(
            "/user/",
            json={"nome": "João Silva", "email": EMAIL_TESTE, "senha": "senha123"},
        )

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_login():
    global TOKEN_GLOBAL  # Permite modificar a variável global

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            "auth/login", json={"email": EMAIL_TESTE, "senha": "senha123"}
        )

        assert response.status_code == 200, f"Erro: {response.text}"

        json_response = response.json()
        assert "access_token" in json_response, "Token não encontrado na resposta"

        # Salva o token para uso nos outros testes
        TOKEN_GLOBAL = json_response["access_token"]
        print(f"Token salvo: {TOKEN_GLOBAL}")  # Apenas para depuração


@pytest.mark.asyncio
async def test_criar_dispositivo():
    global USER_ID_GLOBAL  # Permite modificar a variável global
    global DEVICE_ID_GLOBAL  # Permite modificar a variável global

    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        user_data = await client.get(f"user/email/{EMAIL_TESTE}")
        assert user_data.status_code == 200
        USER_ID_GLOBAL = user_data.json()["id"]

        response = await client.post(
            "/device/",
            json={"nome": "Lâmpada", "usuario_id": USER_ID_GLOBAL},
            headers={"Authorization": f"Bearer {TOKEN_GLOBAL}"},  # Adiciona o token JWT
        )

        assert response.status_code == 200
        data = response.json()
        DEVICE_ID_GLOBAL = data["id"]
        assert data["nome"] == "Lâmpada"
        assert data["usuario_id"] == USER_ID_GLOBAL

        # Salva o token para uso nos outros testes
        print(f"Dispositivo salvo: {data['id']}")  # Apenas para depuração


@pytest.mark.asyncio
async def test_criar_rotina():
    global ROUTINE_ID_GLOBAL  # Permite modificar a variável global

    # ✅ Verifica se as variáveis globais foram definidas corretamente
    assert USER_ID_GLOBAL is not None, "Erro: USER_ID_GLOBAL não foi definido."
    assert DEVICE_ID_GLOBAL is not None, "Erro: DEVICE_ID_GLOBAL não foi definido."
    assert TOKEN_GLOBAL is not None, "Erro: TOKEN_GLOBAL não foi definido."

    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            "/routine/",
            json={
                "nome": "Rotina Noturna",
                "tipo": "imediata",
                "acao": "desativar",
                "usuario_id": USER_ID_GLOBAL,
                "dispositivos_ids": [
                    DEVICE_ID_GLOBAL
                ],  # Certifique-se de que o backend espera um array
                "horario": "2021-10-10T22:00:00",  # ✅ Formato ISO
            },
            headers={
                "Authorization": f"Bearer {TOKEN_GLOBAL}"
            },  # ✅ Token JWT incluído
        )

        # Exibe erro detalhado se falhar
        assert (
            response.status_code == 200
        ), f"Erro: {response.status_code} - {response.text}"

        data = response.json()
        assert data["nome"] == "Rotina Noturna"
        ROUTINE_ID_GLOBAL = data["id"]  # Salva o ID da rotina para testes futuros


@pytest.mark.asyncio
async def test_excluir_usuario():
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(f"user/email/{EMAIL_TESTE}")
        assert response.status_code == 200
        user_id = response.json()["id"]

        response = await client.delete(
            f"/user/{user_id}",
            headers={"Authorization": f"Bearer {TOKEN_GLOBAL}"},
        )

        assert response.status_code == 200
        assert (
            response.json()["mensagem"]
            == "Usuário e dispositivos deletados com sucesso."
        )
