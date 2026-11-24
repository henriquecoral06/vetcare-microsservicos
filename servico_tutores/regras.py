from erros import RegraDeNegocioError
from models import Tutor, db


def _texto(dados, campo):
    return (dados.get(campo) or "").strip()


def criar(dados):
    nome = _texto(dados, "nome")
    cpf = _texto(dados, "cpf")
    telefone = _texto(dados, "telefone")
    email = _texto(dados, "email") or None

    if not nome or not cpf or not telefone:
        raise RegraDeNegocioError("Nome, CPF e telefone são obrigatórios.")
    if Tutor.query.filter_by(cpf=cpf).first():
        raise RegraDeNegocioError("Já existe um tutor com esse CPF.")

    tutor = Tutor(nome=nome, cpf=cpf, telefone=telefone, email=email,
                  ativo=True, saldo_devedor=0.0)
    db.session.add(tutor)
    db.session.commit()
    return tutor


def buscar(tutor_id):
    return db.session.get(Tutor, tutor_id)


def listar():
    return Tutor.query.order_by(Tutor.id).all()


def editar(tutor, dados):
    nome = _texto(dados, "nome")
    telefone = _texto(dados, "telefone")
    if not nome or not telefone:
        raise RegraDeNegocioError("Nome e telefone são obrigatórios.")
    tutor.nome = nome
    tutor.telefone = telefone
    tutor.email = _texto(dados, "email") or None
    db.session.commit()
    return tutor


def inativar(tutor):
    tutor.ativo = False
    db.session.commit()


def movimentar_debito(tutor, tipo, valor):
    """Chamado pelo serviço de CONSULTAS: lança ou estorna o valor de uma consulta."""
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        raise RegraDeNegocioError("O valor deve ser um número.")
    if valor <= 0:
        raise RegraDeNegocioError("O valor deve ser maior que zero.")

    if tipo == "lancar":
        if not tutor.ativo:
            raise RegraDeNegocioError("O tutor está inativo.")
        tutor.saldo_devedor += valor
    elif tipo == "estornar":
        if tutor.saldo_devedor < valor:
            raise RegraDeNegocioError("O estorno é maior que o saldo devedor.")
        tutor.saldo_devedor -= valor
    else:
        raise RegraDeNegocioError("O tipo deve ser 'lancar' ou 'estornar'.")

    db.session.commit()
    return tutor


def criar_dados_de_exemplo():
    if Tutor.query.count() == 0:
        db.session.add(Tutor(nome="Ana Souza", cpf="111.222.333-44",
                             telefone="(48) 99999-1111", email="ana@exemplo.com"))
        db.session.commit()
