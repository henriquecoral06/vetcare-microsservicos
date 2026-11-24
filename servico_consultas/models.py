from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Só os ids. Sem ForeignKey: pets, veterinários e tutores ficam em OUTROS
    # microsserviços, cada um com o seu próprio banco de dados.
    pet_id = db.Column(db.Integer, nullable=False, index=True)
    veterinario_id = db.Column(db.Integer, nullable=False, index=True)
    tutor_id = db.Column(db.Integer, nullable=False, index=True)

    data_hora = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(15), nullable=False, default="agendada")  # agendada ou cancelada
    criada_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def para_dict(self):
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "veterinario_id": self.veterinario_id,
            "tutor_id": self.tutor_id,
            "data_hora": self.data_hora.isoformat(timespec="minutes"),
            "motivo": self.motivo,
            "valor": round(self.valor, 2),
            "status": self.status,
            "criada_em": self.criada_em.isoformat(timespec="seconds"),
        }
