import tutores_helper
from erros import RegraDeNegocioError
from models import ESPECIES, Pet, db


def _texto(dados, campo):
    return (dados.get(campo) or "").strip()


def _idade(dados):
    idade = dados.get("idade")
    if idade is None:
        return None
    if not isinstance(idade, int) or isinstance(idade, bool) or idade < 0:
        raise RegraDeNegocioError("A idade deve ser um número inteiro maior ou igual a zero.")
    return idade


def _dados_basicos(dados):
    nome = _texto(dados, "nome")
    especie = _texto(dados, "especie").lower()
    if not nome:
        raise RegraDeNegocioError("O nome do pet é obrigatório.")
    if especie not in ESPECIES:
        raise RegraDeNegocioError(f"A espécie deve ser uma destas: {', '.join(ESPECIES)}.")
    return nome, especie, _texto(dados, "raca") or None, _idade(dados)


def criar(dados):
    nome, especie, raca, idade = _dados_basicos(dados)
    tutor_id = dados.get("tutor_id")
    if not isinstance(tutor_id, int) or isinstance(tutor_id, bool):
        raise RegraDeNegocioError("O tutor_id deve ser um número inteiro.")

    print(f"[PETS] passo 1: pergunto ao TUTORES se o tutor {tutor_id} existe e está ativo", flush=True)
    tutor = tutores_helper.buscar_tutor(tutor_id)
    if not tutor or not tutor["ativo"]:
        raise RegraDeNegocioError("O tutor não existe ou está inativo.")

    print("[PETS] passo 2: gravo o pet no MEU banco (pets.db)", flush=True)
    pet = Pet(nome=nome, especie=especie, raca=raca, idade=idade, tutor_id=tutor_id, ativo=True)
    db.session.add(pet)
    db.session.commit()
    return pet


def buscar(pet_id):
    return db.session.get(Pet, pet_id)


def buscar_com_tutor(pet):
    """Busca 1: ao consultar o pet, mostra também os dados do tutor."""
    resultado = pet.para_dict()
    try:
        resultado["tutor"] = tutores_helper.buscar_tutor(pet.tutor_id)
    except RegraDeNegocioError as erro:
        # O Tutores caiu: o pet continua sendo mostrado, com um aviso claro.
        resultado["tutor"] = None
        resultado["aviso"] = str(erro)
    return resultado


def listar(tutor_id=None):
    consulta = Pet.query
    if tutor_id is not None:
        consulta = consulta.filter_by(tutor_id=tutor_id)
    return consulta.order_by(Pet.id).all()


def editar(pet, dados):
    pet.nome, pet.especie, pet.raca, pet.idade = _dados_basicos(dados)
    db.session.commit()
    return pet


def inativar(pet):
    pet.ativo = False
    db.session.commit()


def criar_dados_de_exemplo():
    if Pet.query.count() == 0:
        # tutor_id=1 é a tutora de exemplo criada pelo serviço de Tutores.
        db.session.add(Pet(nome="Thor", especie="cachorro", raca="Labrador",
                           idade=4, tutor_id=1))
        db.session.commit()
