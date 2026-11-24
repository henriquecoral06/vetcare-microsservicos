"""O "telefone" do serviço de Consultas para falar com o serviço de Tutores."""
import os

import requests

from erros import RegraDeNegocioError

# Localmente: http://127.0.0.1:5001. No Render: a URL pública, na variável TUTORES_URL.
TUTORES_URL = os.environ.get("TUTORES_URL", "http://127.0.0.1:5001").rstrip("/")
TIMEOUT = 5  # segundos: não esperar para sempre por um serviço lento


def _chamar(metodo, caminho, **kwargs):
    print(f"[CONSULTAS]   >>> ligando para TUTORES: {metodo} {caminho}", flush=True)
    try:
        resposta = requests.request(metodo, TUTORES_URL + caminho, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        print("[CONSULTAS]   <<< TUTORES não atendeu (fora do ar?)", flush=True)
        raise RegraDeNegocioError("O serviço de Tutores está indisponível. Tente mais tarde.")
    except requests.exceptions.Timeout:
        print("[CONSULTAS]   <<< TUTORES demorou demais (timeout)", flush=True)
        raise RegraDeNegocioError("O serviço de Tutores demorou demais (timeout).")
    print(f"[CONSULTAS]   <<< TUTORES respondeu {resposta.status_code}", flush=True)
    return resposta


def _garantir_sucesso(resposta):
    if resposta.ok:
        return
    if resposta.status_code == 400:
        motivo = resposta.json().get("erro", "pedido inválido")
        raise RegraDeNegocioError(f"Tutores recusou: {motivo}")
    raise RegraDeNegocioError(f"O serviço de Tutores respondeu com erro {resposta.status_code}.")


def movimentar_debito(tutor_id, tipo, valor):
    """Alteração (POST): lança ou estorna o valor da consulta no saldo devedor do tutor."""
    corpo = {"tipo": tipo, "valor": valor}
    resposta = _chamar("POST", f"/api/tutores/{tutor_id}/debitos", json=corpo)
    if resposta.status_code == 404:
        raise RegraDeNegocioError("O tutor do pet não foi encontrado.")
    _garantir_sucesso(resposta)
