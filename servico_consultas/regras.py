from datetime import datetime

import pets_helper
import tutores_helper
import veterinarios_helper
from erros import RegraDeNegocioError
from models import Consulta, db


def _inteiro(dados, campo):
    valor = dados.get(campo)
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise RegraDeNegocioError(f"O {campo} deve ser um número inteiro.")
    return valor


def _data_hora(dados):
    try:
        return datetime.fromisoformat(dados.get("data_hora"))
    except (TypeError, ValueError):
        raise RegraDeNegocioError("A data_hora deve estar no formato AAAA-MM-DDTHH:MM.")


def _motivo(dados):
    motivo = (dados.get("motivo") or "").strip()
    if not motivo:
        raise RegraDeNegocioError("O motivo da consulta é obrigatório.")
    return motivo


def agendar(dados):
    pet_id = _inteiro(dados, "pet_id")
    vet_id = _inteiro(dados, "veterinario_id")
    data_hora = _data_hora(dados)
    motivo = _motivo(dados)

    print(f"[CONSULTAS] passo 1: pergunto ao PETS se o pet {pet_id} existe e está ativo", flush=True)
    pet = pets_helper.buscar_pet(pet_id)
    if not pet or not pet["ativo"]:
        raise RegraDeNegocioError("O pet não existe ou está inativo.")

    print(f"[CONSULTAS] passo 2: pergunto ao VETERINARIOS se o veterinário {vet_id} "
          f"está ativo e quanto custa a consulta", flush=True)
    vet = veterinarios_helper.buscar_veterinario(vet_id)
    if not vet or not vet["ativo"]:
        raise RegraDeNegocioError("O veterinário não existe ou está inativo.")

    print("[CONSULTAS] passo 3: gravo a consulta no MEU banco (consultas.db)", flush=True)
    consulta = Consulta(pet_id=pet_id, veterinario_id=vet_id, tutor_id=pet["tutor_id"],
                        data_hora=data_hora, motivo=motivo, valor=vet["valor_consulta"],
                        status="agendada")
    db.session.add(consulta)
    db.session.commit()

    print(f"[CONSULTAS] passo 4: peço ao TUTORES para lançar {consulta.valor:.2f} "
          f"no saldo devedor do tutor {consulta.tutor_id}", flush=True)
    try:
        tutores_helper.movimentar_debito(consulta.tutor_id, "lancar", consulta.valor)
    except Exception:
        # Cada serviço tem seu banco: não existe "desfazer tudo" automático.
        # Se o débito não foi lançado, apagamos a consulta (compensação).
        print("[CONSULTAS] deu errado: apago a consulta gravada (compensação)", flush=True)
        db.session.delete(consulta)
        db.session.commit()
        raise

    print("[CONSULTAS] pronto: consulta agendada", flush=True)
    return consulta


def cancelar(consulta):
    if consulta.status == "cancelada":
        raise RegraDeNegocioError("A consulta já está cancelada.")

    # Primeiro estorna no Tutores; só muda o status aqui se o estorno deu certo.
    print(f"[CONSULTAS] passo 1: peço ao TUTORES para estornar {consulta.valor:.2f} "
          f"do tutor {consulta.tutor_id}", flush=True)
    tutores_helper.movimentar_debito(consulta.tutor_id, "estornar", consulta.valor)

    print("[CONSULTAS] passo 2: marco a consulta como cancelada no MEU banco", flush=True)
    consulta.status = "cancelada"
    db.session.commit()
    return consulta


def buscar(consulta_id):
    return db.session.get(Consulta, consulta_id)


def listar(pet_id=None):
    consulta = Consulta.query
    if pet_id is not None:
        consulta = consulta.filter_by(pet_id=pet_id)
    return consulta.order_by(Consulta.data_hora).all()


def editar(consulta, dados):
    if consulta.status == "cancelada":
        raise RegraDeNegocioError("Não é possível editar uma consulta cancelada.")
    consulta.data_hora = _data_hora(dados)
    consulta.motivo = _motivo(dados)
    db.session.commit()
    return consulta


def criar_dados_de_exemplo():
    # Nenhuma consulta de exemplo: agendar exige lançar o débito no Tutores.
    pass
