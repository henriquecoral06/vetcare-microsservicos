"""O "telefone" do serviço de Consultas para falar com o serviço de Pets."""
import os

import requests

from erros import RegraDeNegocioError

# Localmente: http://127.0.0.1:5002. No Render: a URL pública, na variável PETS_URL.
PETS_URL = os.environ.get("PETS_URL", "http://127.0.0.1:5002").rstrip("/")
TIMEOUT = 5  # segundos: não esperar para sempre por um serviço lento


def _chamar(metodo, caminho, **kwargs):
    print(f"[CONSULTAS]   >>> ligando para PETS: {metodo} {caminho}", flush=True)
    try:
        resposta = requests.request(metodo, PETS_URL + caminho, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        print("[CONSULTAS]   <<< PETS não atendeu (fora do ar?)", flush=True)
        raise RegraDeNegocioError("O serviço de Pets está indisponível. Tente mais tarde.")
    except requests.exceptions.Timeout:
        print("[CONSULTAS]   <<< PETS demorou demais (timeout)", flush=True)
        raise RegraDeNegocioError("O serviço de Pets demorou demais (timeout).")
    print(f"[CONSULTAS]   <<< PETS respondeu {resposta.status_code}", flush=True)
    return resposta


def _garantir_sucesso(resposta):
    if resposta.ok:
        return
    if resposta.status_code == 400:
        motivo = resposta.json().get("erro", "pedido inválido")
        raise RegraDeNegocioError(f"Pets recusou: {motivo}")
    raise RegraDeNegocioError(f"O serviço de Pets respondeu com erro {resposta.status_code}.")


def buscar_pet(pet_id):
    """Busca de apoio (GET): o pet existe e está ativo? Quem é o tutor? None se não existir."""
    resposta = _chamar("GET", f"/api/pets/{pet_id}/resumo")
    if resposta.status_code == 404:
        return None
    _garantir_sucesso(resposta)
    return resposta.json()
