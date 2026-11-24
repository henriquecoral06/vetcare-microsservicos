"""O "telefone" do serviço de Consultas para falar com o serviço de Veterinários."""
import os

import requests

from erros import RegraDeNegocioError

# Localmente: http://127.0.0.1:5003. No Render: a URL pública, na variável VETERINARIOS_URL.
VETERINARIOS_URL = os.environ.get("VETERINARIOS_URL", "http://127.0.0.1:5003").rstrip("/")
TIMEOUT = 5  # segundos: não esperar para sempre por um serviço lento


def _chamar(metodo, caminho, **kwargs):
    print(f"[CONSULTAS]   >>> ligando para VETERINARIOS: {metodo} {caminho}", flush=True)
    try:
        resposta = requests.request(metodo, VETERINARIOS_URL + caminho, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        print("[CONSULTAS]   <<< VETERINARIOS não atendeu (fora do ar?)", flush=True)
        raise RegraDeNegocioError("O serviço de Veterinários está indisponível. Tente mais tarde.")
    except requests.exceptions.Timeout:
        print("[CONSULTAS]   <<< VETERINARIOS demorou demais (timeout)", flush=True)
        raise RegraDeNegocioError("O serviço de Veterinários demorou demais (timeout).")
    print(f"[CONSULTAS]   <<< VETERINARIOS respondeu {resposta.status_code}", flush=True)
    return resposta


def _garantir_sucesso(resposta):
    if resposta.ok:
        return
    if resposta.status_code == 400:
        motivo = resposta.json().get("erro", "pedido inválido")
        raise RegraDeNegocioError(f"Veterinários recusou: {motivo}")
    raise RegraDeNegocioError(f"O serviço de Veterinários respondeu com erro {resposta.status_code}.")


def buscar_veterinario(vet_id):
    """Busca 2 (GET): o veterinário está ativo? Quanto custa a consulta? None se não existir."""
    resposta = _chamar("GET", f"/api/veterinarios/{vet_id}")
    if resposta.status_code == 404:
        return None
    _garantir_sucesso(resposta)
    return resposta.json()
