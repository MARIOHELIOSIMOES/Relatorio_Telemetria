import getpass
import bcrypt
from datetime import datetime

from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from flask_migrate import Migrate

import config

from database.models import (
    db,
    Usuario,
    Aviso,
    Relatorio
)


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
# ROTA PRINCIPAL - DASHBOARD
# ============================================================

@app.route("/")
@login_required
def index():

    from utils.turnos import (
        obter_turno,
        obter_horario_turno
    )

    # ========================================================
    # TURNO
    # ========================================================

    turno_atual = obter_turno()

    horario_turno = obter_horario_turno(
        turno_atual
    )

    # ========================================================
    # DATA ATUAL
    # ========================================================

    hoje = datetime.now().date()

    inicio_dia = datetime.combine(
        hoje,
        datetime.min.time()
    )

    fim_dia = datetime.combine(
        hoje,
        datetime.max.time()
    )

    # ========================================================
    # INDICADORES
    # ========================================================

    # --------------------------------------------------------
    # TOTAL DE RELATÓRIOS DO DIA
    # --------------------------------------------------------

    total_relatorios = db.session.scalar(
        db.select(
            db.func.count(Relatorio.id)
        ).where(
            Relatorio.data_hora >= inicio_dia,
            Relatorio.data_hora <= fim_dia
        )
    ) or 0


    # --------------------------------------------------------
    # RELATÓRIOS POR TURNO
    # --------------------------------------------------------

    relatorios_turno_1 = db.session.scalar(
        db.select(
            db.func.count(Relatorio.id)
        ).where(
            Relatorio.data_hora >= inicio_dia,
            Relatorio.data_hora <= fim_dia,
            Relatorio.turno == "1"
        )
    ) or 0


    relatorios_turno_2 = db.session.scalar(
        db.select(
            db.func.count(Relatorio.id)
        ).where(
            Relatorio.data_hora >= inicio_dia,
            Relatorio.data_hora <= fim_dia,
            Relatorio.turno == "2"
        )
    ) or 0


    relatorios_turno_3 = db.session.scalar(
        db.select(
            db.func.count(Relatorio.id)
        ).where(
            Relatorio.data_hora >= inicio_dia,
            Relatorio.data_hora <= fim_dia,
            Relatorio.turno == "3"
        )
    ) or 0


    # --------------------------------------------------------
    # AVISOS ATIVOS
    # --------------------------------------------------------

    total_avisos = db.session.scalar(
        db.select(
            db.func.count(Aviso.id)
        ).where(
            Aviso.ativo.is_(True)
        )
    ) or 0


    # --------------------------------------------------------
    # USUÁRIOS ATIVOS
    # --------------------------------------------------------

    total_usuarios = db.session.scalar(
        db.select(
            db.func.count(Usuario.id)
        ).where(
            Usuario.ativo.is_(True)
        )
    ) or 0
    # ========================================================
    # RELATÓRIOS POR TURNO
    # ========================================================

    relatorios_turno_1 = db.session.scalar(
        db.select(
            db.func.count(Relatorio.id)
        ).where(
            Relatorio.data_hora >= inicio_dia,
            Relatorio.data_hora <= fim_dia,
            Relatorio.turno == "1"
        )
    ) or 0

    relatorios_turno_2 = db.session.scalar(
        db.select(
            db.func.count(Relatorio.id)
        ).where(
            Relatorio.data_hora >= inicio_dia,
            Relatorio.data_hora <= fim_dia,
            Relatorio.turno == "2"
        )
    ) or 0

    relatorios_turno_3 = db.session.scalar(
        db.select(
            db.func.count(Relatorio.id)
        ).where(
            Relatorio.data_hora >= inicio_dia,
            Relatorio.data_hora <= fim_dia,
            Relatorio.turno == "3"
        )
    ) or 0

    relatorios_turno_4 = db.session.scalar(
        db.select(
            db.func.count(Relatorio.id)
        ).where(
            Relatorio.data_hora >= inicio_dia,
            Relatorio.data_hora <= fim_dia,
            Relatorio.turno == "4"
        )
    ) or 0



    # ========================================================
    # AVISOS RECENTES
    # ========================================================

    avisos_recentes = (
        db.session.scalars(
            db.select(Aviso)
            .where(
                Aviso.ativo.is_(True)
            )
            .order_by(
                Aviso.data_criacao.desc()
            )
            .limit(3)
        )
        .all()
    )

    # ========================================================
    # DASHBOARD
    # ========================================================

    return render_template(
        "dashboard.html",

        turno_atual=turno_atual,

        horario_turno=horario_turno,

        total_relatorios=total_relatorios,

        total_avisos=total_avisos,

        total_usuarios=total_usuarios,

        relatorios_turno_1=relatorios_turno_1,

        relatorios_turno_2=relatorios_turno_2,

        relatorios_turno_3=relatorios_turno_3,

        relatorios_turno_4=relatorios_turno_4,

        avisos_recentes=avisos_recentes
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
        host="0.0.0.0"
        port=8000
    )