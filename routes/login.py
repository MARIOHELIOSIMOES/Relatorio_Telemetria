from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    current_user
)

from database.models import db, Usuario


login_bp = Blueprint(
    "login",
    __name__
)


# ============================================================
# LOGIN
# ============================================================

@login_bp.route("/login", methods=["GET", "POST"])
def login():

    # --------------------------------------------------------
    # Se já estiver autenticado, vai para o painel
    # --------------------------------------------------------

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    # --------------------------------------------------------
    # POST - tentativa de login
    # --------------------------------------------------------

    if request.method == "POST":

        usuario = request.form.get(
            "usuario",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        )

        # ----------------------------------------------------
        # Validação básica
        # ----------------------------------------------------

        if not usuario or not senha:

            flash(
                "Informe o usuário e a senha.",
                "warning"
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # Busca usuário
        # ----------------------------------------------------

        usuario_obj = db.session.scalar(
            db.select(Usuario).where(
                Usuario.usuario == usuario
            )
        )

        # ----------------------------------------------------
        # Usuário inexistente
        # ----------------------------------------------------

        if usuario_obj is None:

            flash(
                "Usuário ou senha inválidos.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # Usuário inativo
        # ----------------------------------------------------

        if not usuario_obj.ativo:

            flash(
                "Este usuário está inativo. "
                "Entre em contato com o administrador.",
                "warning"
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # Verifica senha
        # ----------------------------------------------------

        if not usuario_obj.verificar_senha(senha):

            flash(
                "Usuário ou senha inválidos.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # Login realizado
        # ----------------------------------------------------

        login_user(usuario_obj)

        usuario_obj.ultimo_login = datetime.utcnow()

        db.session.commit()

        # ----------------------------------------------------
        # Redireciona
        # ----------------------------------------------------

        return redirect(
            url_for("index")
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@login_bp.route("/logout")
def logout():

    if current_user.is_authenticated:

        logout_user()

    return redirect(
        url_for("login.login")
    )