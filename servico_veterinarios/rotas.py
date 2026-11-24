from flask import Blueprint, jsonify, request

import regras

rotas = Blueprint("veterinarios", __name__, url_prefix="/api/veterinarios")


def nao_encontrado():
    return jsonify(erro="Veterinário não encontrado."), 404


@rotas.post("")
def criar():
    vet = regras.criar(request.get_json(silent=True) or {})
    return jsonify(vet.para_dict()), 201


@rotas.get("")
def listar():
    return jsonify([v.para_dict() for v in regras.listar()])


# Também é a rota que o serviço de CONSULTAS chama (Busca 2).
@rotas.get("/<int:vet_id>")
def buscar(vet_id):
    vet = regras.buscar(vet_id)
    return jsonify(vet.para_dict()) if vet else nao_encontrado()


@rotas.put("/<int:vet_id>")
def editar(vet_id):
    vet = regras.buscar(vet_id)
    if not vet:
        return nao_encontrado()
    return jsonify(regras.editar(vet, request.get_json(silent=True) or {}).para_dict())


@rotas.delete("/<int:vet_id>")
def inativar(vet_id):
    vet = regras.buscar(vet_id)
    if not vet:
        return nao_encontrado()
    regras.inativar(vet)
    return "", 204
