from erros import RegraDeNegocioError
from models import Veterinario, db


def _texto(dados, campo):
    return (dados.get(campo) or "").strip()


def _valor(dados):
    try:
        valor = float(dados.get("valor_consulta"))
    except (TypeError, ValueError):
        raise RegraDeNegocioError("O valor_consulta deve ser um número.")
    if valor <= 0:
        raise RegraDeNegocioError("O valor_consulta deve ser maior que zero.")
    return valor


def criar(dados):
    nome = _texto(dados, "nome")
    crmv = _texto(dados, "crmv")
    especialidade = _texto(dados, "especialidade")
    if not nome or not crmv or not especialidade:
        raise RegraDeNegocioError("Nome, CRMV e especialidade são obrigatórios.")
    valor = _valor(dados)
    if Veterinario.query.filter_by(crmv=crmv).first():
        raise RegraDeNegocioError("Já existe um veterinário com esse CRMV.")

    vet = Veterinario(nome=nome, crmv=crmv, especialidade=especialidade,
                      valor_consulta=valor, ativo=True)
    db.session.add(vet)
    db.session.commit()
    return vet


def buscar(vet_id):
    return db.session.get(Veterinario, vet_id)


def listar():
    return Veterinario.query.order_by(Veterinario.id).all()


def editar(vet, dados):
    nome = _texto(dados, "nome")
    especialidade = _texto(dados, "especialidade")
    if not nome or not especialidade:
        raise RegraDeNegocioError("Nome e especialidade são obrigatórios.")
    vet.nome = nome
    vet.especialidade = especialidade
    vet.valor_consulta = _valor(dados)
    db.session.commit()
    return vet


def inativar(vet):
    vet.ativo = False
    db.session.commit()


def criar_dados_de_exemplo():
    if Veterinario.query.count() == 0:
        db.session.add(Veterinario(nome="Dr. Carlos Lima", crmv="SC-12345",
                                   especialidade="Clínica geral", valor_consulta=150.0))
        db.session.commit()
