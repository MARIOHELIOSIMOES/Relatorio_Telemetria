import bcrypt
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


# ============================================================
# USUÁRIOS
# ============================================================

class Usuario(UserMixin, db.Model):

    __tablename__ = "usuarios"
    __table_args__ = {"schema": "tele"}

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    usuario = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    senha_hash = db.Column(
        db.String(255),
        nullable=False
    )

    email = db.Column(
        db.String(150)
    )

    administrador = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    data_cadastro = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    ultimo_login = db.Column(
        db.DateTime
    )

    # ========================================================
    # RELACIONAMENTOS
    # ========================================================

    avisos_criados = db.relationship(
        "Aviso",
        foreign_keys="Aviso.usuario_id",
        back_populates="criador",
        lazy=True
    )

    avisos_inativados = db.relationship(
        "Aviso",
        foreign_keys="Aviso.usuario_inativacao",
        back_populates="inativador",
        lazy=True
    )

    relatorios = db.relationship(
        "Relatorio",
        back_populates="usuario",
        lazy=True
    )

    logs = db.relationship(
        "Log",
        back_populates="usuario",
        lazy=True
    )

    # ========================================================

    def __repr__(self):
        return f"<Usuario {self.usuario}>"

    def get_id(self):
        return str(self.id)

    def definir_senha(self, senha):
        self.senha_hash = bcrypt.hashpw(
            senha.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")


    def verificar_senha(self, senha):
        return bcrypt.checkpw(
            senha.encode("utf-8"),
            self.senha_hash.encode("utf-8")
        )
# ============================================================
# AVISOS
# ============================================================

class Aviso(db.Model):

    __tablename__ = "avisos"
    __table_args__ = {"schema": "tele"}

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    titulo = db.Column(
        db.String(200),
        nullable=False
    )

    texto = db.Column(
        db.Text,
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("tele.usuarios.id"),
        nullable=False
    )

    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    data_inativacao = db.Column(
        db.DateTime
    )

    usuario_inativacao = db.Column(
        db.Integer,
        db.ForeignKey("tele.usuarios.id")
    )

    # ========================================================
    # RELACIONAMENTOS
    # ========================================================

    criador = db.relationship(
        "Usuario",
        foreign_keys=[usuario_id],
        back_populates="avisos_criados"
    )

    inativador = db.relationship(
        "Usuario",
        foreign_keys=[usuario_inativacao],
        back_populates="avisos_inativados"
    )

    # ========================================================

    def __repr__(self):
        return f"<Aviso {self.titulo}>"


# ============================================================
# RELATÓRIOS
# ============================================================

class Relatorio(db.Model):

    __tablename__ = "relatorios"
    __table_args__ = {"schema": "tele"}

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("tele.usuarios.id"),
        nullable=False
    )

    data_hora = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    turno = db.Column(
        db.String(1),
        nullable=False
    )

    descricao = db.Column(
        db.Text,
        nullable=False
    )

    # ========================================================
    # RELACIONAMENTO
    # ========================================================

    usuario = db.relationship(
        "Usuario",
        back_populates="relatorios"
    )

    # ========================================================

    def __repr__(self):
        return f"<Relatorio {self.id}>"


# ============================================================
# LOGS
# ============================================================

class Log(db.Model):

    __tablename__ = "logs"
    __table_args__ = {"schema": "tele"}

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("tele.usuarios.id")
    )

    data_hora = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    acao = db.Column(
        db.String(300)
    )

    ip = db.Column(
        db.String(50)
    )

    detalhes = db.Column(
        db.Text
    )

    # ========================================================
    # RELACIONAMENTO
    # ========================================================

    usuario = db.relationship(
        "Usuario",
        back_populates="logs"
    )

    # ========================================================

    def __repr__(self):
        return f"<Log {self.id}>"