from flask import Blueprint, jsonify, request

import regras

rotas = Blueprint("pets", __name__, url_prefix="/api/pets")


def nao_encontrado():
    return jsonify(erro="Pet não encontrado."), 404


@rotas.post("")
def criar():
    pet = regras.criar(request.get_json(silent=True) or {})
    return jsonify(pet.para_dict()), 201


@rotas.get("")
def listar():
    tutor_id = request.args.get("tutor_id", type=int)
    return jsonify([p.para_dict() for p in regras.listar(tutor_id)])


# Busca 1: devolve o pet junto com os dados do tutor (vindos do serviço de Tutores).
@rotas.get("/<int:pet_id>")
def buscar(pet_id):
    pet = regras.buscar(pet_id)
    return jsonify(regras.buscar_com_tutor(pet)) if pet else nao_encontrado()


# Versão "simples", sem chamar ninguém. É a rota que o serviço de CONSULTAS usa.
@rotas.get("/<int:pet_id>/resumo")
def resumo(pet_id):
    pet = regras.buscar(pet_id)
    return jsonify(pet.para_dict()) if pet else nao_encontrado()


@rotas.put("/<int:pet_id>")
def editar(pet_id):
    pet = regras.buscar(pet_id)
    if not pet:
        return nao_encontrado()
    return jsonify(regras.editar(pet, request.get_json(silent=True) or {}).para_dict())


@rotas.delete("/<int:pet_id>")
def inativar(pet_id):
    pet = regras.buscar(pet_id)
    if not pet:
        return nao_encontrado()
    regras.inativar(pet)
    return "", 204
