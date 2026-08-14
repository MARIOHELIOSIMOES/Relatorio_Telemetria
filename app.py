import getpass
import bcrypt

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

import config

from database.models import db, Usuario


# ============================================================
# APLICAÇÃO FLASK
# ============================================================

app = Flask(__name__)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

app.config["SECRET_KEY"] = config.SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = (
    config.SQLALCHEMY_DATABASE_URI
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = (
    config.SQLALCHEMY_TRACK_MODIFICATIONS
)


# ============================================================
# BANCO DE DADOS
# ============================================================

db.init_app(app)


# ============================================================
# MIGRAÇÕES
# ============================================================

migrate = Migrate(
    app,
    db
)


# ============================================================
# LOGIN
# ============================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login.login"

login_manager.login_message = (
    "Faça login para acessar o sistema."
)

login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        Usuario,
        int(user_id)
    )


# ============================================================
# BLUEPRINTS
# ============================================================

from routes.login import login_bp
from routes.relatorios import relatorios_bp
from routes.avisos import avisos_bp
from routes.usuarios import usuarios_bp
from routes.admin import admin_bp

app.register_blueprint(login_bp)
app.register_blueprint(relatorios_bp)
app.register_blueprint(avisos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(admin_bp)


# ============================================================
# ROTA PRINCIPAL
# ============================================================

@app.route("/")
def index():

    from flask import redirect, url_for, render_template
    from flask_login import current_user

    if not current_user.is_authenticated:
        return redirect(
            url_for("login.login")
        )

    from utils.turnos import (
        obter_turno,
        obter_horario_turno
    )

    turno_atual = obter_turno()

    horario_turno = obter_horario_turno(
        turno_atual
    )

    return render_template(
        "dashboard.html",
        turno_atual=turno_atual,
        horario_turno=horario_turno
    )


# ============================================================
# COMANDO - CRIAR ADMINISTRADOR
# ============================================================

@app.cli.command("criar-admin")
def criar_admin():

    print()
    print("=" * 50)
    print(" CRIAÇÃO DO ADMINISTRADOR")
    print("=" * 50)
    print()

    nome = input("Nome: ").strip()
    usuario = input("Usuário: ").strip()

    if not nome:
        print("ERRO: o nome é obrigatório.")
        return

    if not usuario:
        print("ERRO: o usuário é obrigatório.")
        return

    # --------------------------------------------------------
    # Verifica se o usuário já existe
    # --------------------------------------------------------

    usuario_existente = db.session.scalar(
        db.select(Usuario).where(
            Usuario.usuario == usuario
        )
    )

    if usuario_existente:
        print()
        print("ERRO: este usuário já existe.")
        return

    # --------------------------------------------------------
    # Senha
    # --------------------------------------------------------

    senha = getpass.getpass("Senha: ")
    confirmacao = getpass.getpass("Confirmar senha: ")

    if not senha:
        print()
        print("ERRO: a senha não pode ser vazia.")
        return

    if senha != confirmacao:
        print()
        print("ERRO: as senhas não conferem.")
        return

    # --------------------------------------------------------
    # Cria hash da senha
    # --------------------------------------------------------

    senha_hash = bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # --------------------------------------------------------
    # Cria usuário
    # --------------------------------------------------------

    novo_usuario = Usuario(
        nome=nome,
        usuario=usuario,
        senha_hash=senha_hash,
        administrador=True,
        ativo=True
    )

    db.session.add(novo_usuario)
    db.session.commit()

    print()
    print("=" * 50)
    print(" ADMINISTRADOR CRIADO COM SUCESSO!")
    print("=" * 50)
    print()
    print(f"Nome:    {nome}")
    print(f"Usuário: {usuario}")
    print()

# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )