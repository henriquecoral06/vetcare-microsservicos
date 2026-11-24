import logging

from flask import Flask, jsonify, request

import regras
from erros import RegraDeNegocioError
from models import db
from rotas import rotas

NOME = "VETERINARIOS"
PORTA = 5003

logging.getLogger("werkzeug").setLevel(logging.ERROR)  # esconde o log padrão do Flask


def criar_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.sort_keys = False

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///veterinarios.db"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        regras.criar_dados_de_exemplo()  # no Render o disco é temporário

    app.register_blueprint(rotas)

    @app.get("/api/health")
    def health():
        return jsonify(status="no ar", servico=NOME)

    @app.after_request
    def mostrar_no_terminal(resposta):
        print(f"[{NOME}] recebi {request.method} {request.path} "
              f"-> respondi {resposta.status_code}", flush=True)
        return resposta

    @app.errorhandler(RegraDeNegocioError)
    def erro_de_regra(erro):
        print(f"[{NOME}] regra violada: {erro}", flush=True)
        return jsonify(erro=str(erro)), 400

    return app


# O Render (gunicorn app:app) procura esta variável. Não remover.
app = criar_app()

if __name__ == "__main__":
    print(f"[{NOME}] iniciando na porta {PORTA}...", flush=True)
    app.run(port=PORTA, debug=True)
