"""O "telefone" do serviço de Pets para falar com o serviço de Tutores."""
import os

import requests

from erros import RegraDeNegocioError

# Localmente: http://127.0.0.1:5001. No Render: a URL pública, na variável TUTORES_URL.
TUTORES_URL = os.environ.get("TUTORES_URL", "http://127.0.0.1:5001").rstrip("/")
TIMEOUT = 5  # segundos: não esperar para sempre por um serviço lento


def _chamar(metodo, caminho, **kwargs):
    print(f"[PETS]   >>> ligando para TUTORES: {metodo} {caminho}", flush=True)
    try:
        resposta = requests.request(metodo, TUTORES_URL + caminho, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        print("[PETS]   <<< TUTORES não atendeu (fora do ar?)", flush=True)
        raise RegraDeNegocioError("O serviço de Tutores está indisponível. Tente mais tarde.")
    except requests.exceptions.Timeout:
        print("[PETS]   <<< TUTORES demorou demais (timeout)", flush=True)
        raise RegraDeNegocioError("O serviço de Tutores demorou demais (timeout).")
    print(f"[PETS]   <<< TUTORES respondeu {resposta.status_code}", flush=True)
    return resposta


def buscar_tutor(tutor_id):
    """Busca 1: devolve os dados do tutor, ou None se ele não existir."""
    resposta = _chamar("GET", f"/api/tutores/{tutor_id}")
    if resposta.status_code == 404:
        return None
    if not resposta.ok:
        raise RegraDeNegocioError(f"O serviço de Tutores respondeu com erro {resposta.status_code}.")
    return resposta.json()
