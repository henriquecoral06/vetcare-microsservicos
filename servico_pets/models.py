from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

ESPECIES = ("cachorro", "gato", "ave", "roedor", "outro")


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    especie = db.Column(db.String(20), nullable=False)
    raca = db.Column(db.String(60), nullable=True)
    idade = db.Column(db.Integer, nullable=True)

    # Só o id do tutor. Sem ForeignKey: a tabela de tutores fica em OUTRO
    # microsserviço, com OUTRO banco de dados (tutores.db).
    tutor_id = db.Column(db.Integer, nullable=False, index=True)

    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def para_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "especie": self.especie,
            "raca": self.raca,
            "idade": self.idade,
            "tutor_id": self.tutor_id,
            "ativo": self.ativo,
        }
