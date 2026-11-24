from flask import Blueprint, jsonify, request

import regras

rotas = Blueprint("consultas", __name__, url_prefix="/api/consultas")


def nao_encontrada():
    return jsonify(erro="Consulta não encontrada."), 404


# Usa as 3 integrações: Pets (GET), Veterinários (GET) e Tutores (POST).
@rotas.post("")
def agendar():
    consulta = regras.agendar(request.get_json(silent=True) or {})
    return jsonify(consulta.para_dict()), 201


@rotas.get("")
def listar():
    pet_id = request.args.get("pet_id", type=int)
    return jsonify([c.para_dict() for c in regras.listar(pet_id)])


@rotas.get("/<int:consulta_id>")
def buscar(consulta_id):
    consulta = regras.buscar(consulta_id)
    return jsonify(consulta.para_dict()) if consulta else nao_encontrada()


@rotas.put("/<int:consulta_id>")
def editar(consulta_id):
    consulta = regras.buscar(consulta_id)
    if not consulta:
        return nao_encontrada()
    return jsonify(regras.editar(consulta, request.get_json(silent=True) or {}).para_dict())


# Cancelar estorna o valor no Tutores (outra alteração entre serviços).
@rotas.patch("/<int:consulta_id>/cancelar")
def cancelar(consulta_id):
    consulta = regras.buscar(consulta_id)
    if not consulta:
        return nao_encontrada()
    return jsonify(regras.cancelar(consulta).para_dict())
