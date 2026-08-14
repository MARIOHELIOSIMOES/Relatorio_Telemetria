from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from database.models import db, Usuario


usuarios_bp = Blueprint(
    "usuarios",
    __name__,
    url_prefix="/admin/usuarios"
)


# ============================================================
# VERIFICAÇÃO DE ADMINISTRADOR
# ============================================================

def administrador_required():

    if not current_user.is_authenticated:
        return False

    return current_user.administrador


# ============================================================
# LISTA DE USUÁRIOS
# ============================================================

@usuarios_bp.route("/")
@login_required
def admin():

    if not administrador_required():
        return "Acesso negado.", 403

    usuarios = db.session.scalars(
        db.select(Usuario)
        .order_by(Usuario.nome)
    ).all()

    return render_template(
        "usuarios/admin.html",
        usuarios=usuarios
    )


# ============================================================
# NOVO USUÁRIO
# ============================================================

@usuarios_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():

    if not administrador_required():
        return "Acesso negado.", 403

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()

        usuario = request.form.get(
            "usuario",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        )

        confirmar_senha = request.form.get(
            "confirmar_senha",
            ""
        )

        administrador = (
            request.form.get("administrador")
            == "on"
        )

        ativo = (
            request.form.get("ativo")
            == "on"
        )

        # ----------------------------------------------------
        # VALIDAÇÕES
        # ----------------------------------------------------

        if not nome:

            flash(
                "O nome é obrigatório.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html"
            )

        if not usuario:

            flash(
                "O usuário é obrigatório.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html"
            )

        if not senha:

            flash(
                "A senha é obrigatória.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html"
            )

        if senha != confirmar_senha:

            flash(
                "As senhas não conferem.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html"
            )

        # ----------------------------------------------------
        # VERIFICA USUÁRIO EXISTENTE
        # ----------------------------------------------------

        usuario_existente = db.session.scalar(
            db.select(Usuario).where(
                Usuario.usuario == usuario
            )
        )

        if usuario_existente:

            flash(
                "Este nome de usuário já está cadastrado.",
                "danger"
            )

            return render_template(
                "usuarios/novo.html"
            )

        # ----------------------------------------------------
        # CRIA USUÁRIO
        # ----------------------------------------------------

        novo_usuario = Usuario(
            nome=nome,
            usuario=usuario,
            email=email if email else None,
            administrador=administrador,
            ativo=ativo
        )

        novo_usuario.definir_senha(
            senha
        )

        db.session.add(
            novo_usuario
        )

        db.session.commit()

        flash(
            "Usuário criado com sucesso.",
            "success"
        )

        return redirect(
            url_for("usuarios.admin")
        )

    return render_template(
        "usuarios/novo.html"
    )


# ============================================================
# EDITAR USUÁRIO
# ============================================================

@usuarios_bp.route(
    "/editar/<int:user_id>",
    methods=["GET", "POST"]
)
@login_required
def editar(user_id):

    if not administrador_required():
        return "Acesso negado.", 403

    usuario = db.session.get(
        Usuario,
        user_id
    )

    if not usuario:
        return "Usuário não encontrado.", 404

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        administrador = (
            request.form.get("administrador")
            == "on"
        )

        ativo = (
            request.form.get("ativo")
            == "on"
        )

        if not nome:

            flash(
                "O nome é obrigatório.",
                "danger"
            )

            return render_template(
                "usuarios/editar.html",
                usuario=usuario
            )

        # ----------------------------------------------------
        # EVITA QUE O ÚLTIMO ADMINISTRADOR SEJA INATIVADO
        # ----------------------------------------------------

        if (
            usuario.administrador
            and not administrador
        ):

            total_admins = db.session.scalar(
                db.select(
                    db.func.count(Usuario.id)
                ).where(
                    Usuario.administrador.is_(True),
                    Usuario.ativo.is_(True)
                )
            )

            if total_admins <= 1:

                flash(
                    "Não é possível remover o último administrador ativo.",
                    "danger"
                )

                return render_template(
                    "usuarios/editar.html",
                    usuario=usuario
                )

        # ----------------------------------------------------
        # EVITA INATIVAR O ÚLTIMO ADMINISTRADOR
        # ----------------------------------------------------

        if (
            usuario.administrador
            and usuario.ativo
            and not ativo
        ):

            total_admins = db.session.scalar(
                db.select(
                    db.func.count(Usuario.id)
                ).where(
                    Usuario.administrador.is_(True),
                    Usuario.ativo.is_(True)
                )
            )

            if total_admins <= 1:

                flash(
                    "Não é possível inativar o último administrador ativo.",
                    "danger"
                )

                return render_template(
                    "usuarios/editar.html",
                    usuario=usuario
                )

        # ----------------------------------------------------
        # ATUALIZA
        # ----------------------------------------------------

        usuario.nome = nome

        usuario.email = (
            email
            if email
            else None
        )

        usuario.administrador = administrador

        usuario.ativo = ativo

        db.session.commit()

        flash(
            "Usuário atualizado com sucesso.",
            "success"
        )

        return redirect(
            url_for("usuarios.admin")
        )

    return render_template(
        "usuarios/editar.html",
        usuario=usuario
    )


# ============================================================
# REDEFINIR SENHA
# ============================================================

@usuarios_bp.route(
    "/senha/<int:user_id>",
    methods=["GET", "POST"]
)
@login_required
def senha(user_id):

    if not administrador_required():
        return "Acesso negado.", 403

    usuario = db.session.get(
        Usuario,
        user_id
    )

    if not usuario:
        return "Usuário não encontrado.", 404

    if request.method == "POST":

        nova_senha = request.form.get(
            "senha",
            ""
        )

        confirmar_senha = request.form.get(
            "confirmar_senha",
            ""
        )

        if not nova_senha:

            flash(
                "A senha não pode ser vazia.",
                "danger"
            )

            return render_template(
                "usuarios/senha.html",
                usuario=usuario
            )

        if nova_senha != confirmar_senha:

            flash(
                "As senhas não conferem.",
                "danger"
            )

            return render_template(
                "usuarios/senha.html",
                usuario=usuario
            )

        usuario.definir_senha(
            nova_senha
        )

        db.session.commit()

        flash(
            "Senha alterada com sucesso.",
            "success"
        )

        return redirect(
            url_for("usuarios.admin")
        )

    return render_template(
        "usuarios/senha.html",
        usuario=usuario
    )