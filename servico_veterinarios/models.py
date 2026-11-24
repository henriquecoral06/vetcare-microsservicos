from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Veterinario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    crmv = db.Column(db.String(20), nullable=False, unique=True)
    especialidade = db.Column(db.String(60), nullable=False)
    valor_consulta = db.Column(db.Float, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def para_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "crmv": self.crmv,
            "especialidade": self.especialidade,
            "valor_consulta": round(self.valor_consulta, 2),
            "ativo": self.ativo,
        }
