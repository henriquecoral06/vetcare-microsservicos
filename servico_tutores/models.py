from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    # Valor que o tutor deve à clínica. É alterado pelo serviço de CONSULTAS.
    saldo_devedor = db.Column(db.Float, nullable=False, default=0.0)

    def para_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "telefone": self.telefone,
            "email": self.email,
            "ativo": self.ativo,
            "saldo_devedor": round(self.saldo_devedor, 2),
        }
