from flask import Blueprint, jsonify, request

import regras

rotas = Blueprint("tutores", __name__, url_prefix="/api/tutores")


def nao_encontrado():
    return jsonify(erro="Tutor não encontrado."), 404


@rotas.post("")
def criar():
    tutor = regras.criar(request.get_json(silent=True) or {})
    return jsonify(tutor.para_dict()), 201


@rotas.get("")
def listar():
    return jsonify([t.para_dict() for t in regras.listar()])


# Também é a rota que o serviço de PETS chama (Busca 1).
@rotas.get("/<int:tutor_id>")
def buscar(tutor_id):
    tutor = regras.buscar(tutor_id)
    return jsonify(tutor.para_dict()) if tutor else nao_encontrado()


@rotas.put("/<int:tutor_id>")
def editar(tutor_id):
    tutor = regras.buscar(tutor_id)
    if not tutor:
        return nao_encontrado()
    return jsonify(regras.editar(tutor, request.get_json(silent=True) or {}).para_dict())


@rotas.delete("/<int:tutor_id>")
def inativar(tutor_id):
    tutor = regras.buscar(tutor_id)
    if not tutor:
        return nao_encontrado()
    regras.inativar(tutor)
    return "", 204


# ---- Rota que o serviço de CONSULTAS chama (Alteração) ----

@rotas.post("/<int:tutor_id>/debitos")
def movimentar_debito(tutor_id):
    tutor = regras.buscar(tutor_id)
    if not tutor:
        return nao_encontrado()
    dados = request.get_json(silent=True) or {}
    regras.movimentar_debito(tutor, dados.get("tipo"), dados.get("valor"))
    return jsonify(tutor.para_dict())
