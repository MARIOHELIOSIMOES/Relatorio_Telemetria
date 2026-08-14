from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from database.models import (
    db,
    Aviso
)


# ============================================================
# BLUEPRINT
# ============================================================

avisos_bp = Blueprint(
    "avisos",
    __name__,
    url_prefix="/avisos"
)


# ============================================================
# FUNÇÃO AUXILIAR
# VERIFICA SE O USUÁRIO É ADMINISTRADOR
# ============================================================

def administrador_required():

    if not current_user.is_authenticated:
        abort(401)

    if not current_user.administrador:
        abort(403)


# ============================================================
# QUADRO DE AVISOS
# SOMENTE AVISOS ATIVOS
# ============================================================

@avisos_bp.route("/")
@login_required
def lista():

    avisos = (
        Aviso.query
        .filter_by(ativo=True)
        .order_by(
            Aviso.data_criacao.desc()
        )
        .all()
    )

    return render_template(
        "avisos.html",
        avisos=avisos
    )


# ============================================================
# ADMINISTRAÇÃO DE AVISOS
# MOSTRA ATIVOS E INATIVOS
# ============================================================

@avisos_bp.route("/admin")
@login_required
def admin():

    administrador_required()

    avisos = (
        Aviso.query
        .order_by(
            Aviso.data_criacao.desc()
        )
        .all()
    )

    return render_template(
        "avisos_admin.html",
        avisos=avisos
    )


# ============================================================
# NOVO AVISO
# ============================================================

@avisos_bp.route(
    "/novo",
    methods=["GET", "POST"]
)
@login_required
def novo():

    administrador_required()

    if request.method == "POST":

        titulo = request.form.get(
            "titulo",
            ""
        ).strip()

        texto = request.form.get(
            "texto",
            ""
        ).strip()

        # ----------------------------------------------------
        # VALIDAÇÃO
        # ----------------------------------------------------

        if not titulo:

            flash(
                "O título do aviso é obrigatório.",
                "warning"
            )

            return render_template(
                "aviso_form.html",
                titulo=titulo,
                texto=texto
            )

        if not texto:

            flash(
                "O texto do aviso é obrigatório.",
                "warning"
            )

            return render_template(
                "aviso_form.html",
                titulo=titulo,
                texto=texto
            )

        # ----------------------------------------------------
        # CRIA AVISO
        # ----------------------------------------------------

        aviso = Aviso(
            titulo=titulo,
            texto=texto,
            usuario_id=current_user.id,
            data_criacao=datetime.utcnow(),
            ativo=True
        )

        db.session.add(aviso)

        db.session.commit()

        flash(
            "Aviso publicado com sucesso!",
            "success"
        )

        return redirect(
            url_for("avisos.admin")
        )

    return render_template(
        "aviso_form.html",
        titulo="",
        texto=""
    )


# ============================================================
# EDITAR AVISO
# ============================================================

@avisos_bp.route(
    "/<int:aviso_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar(aviso_id):

    administrador_required()

    aviso = db.session.get(
        Aviso,
        aviso_id
    )

    if aviso is None:
        abort(404)

    # --------------------------------------------------------
    # FORMULÁRIO
    # --------------------------------------------------------

    if request.method == "POST":

        titulo = request.form.get(
            "titulo",
            ""
        ).strip()

        texto = request.form.get(
            "texto",
            ""
        ).strip()

        # ----------------------------------------------------
        # VALIDAÇÃO
        # ----------------------------------------------------

        if not titulo:

            flash(
                "O título do aviso é obrigatório.",
                "warning"
            )

            return render_template(
                "aviso_form.html",
                aviso=aviso,
                titulo=titulo,
                texto=texto,
                editar=True
            )

        if not texto:

            flash(
                "O texto do aviso é obrigatório.",
                "warning"
            )

            return render_template(
                "aviso_form.html",
                aviso=aviso,
                titulo=titulo,
                texto=texto,
                editar=True
            )

        # ----------------------------------------------------
        # ATUALIZA
        # ----------------------------------------------------

        aviso.titulo = titulo
        aviso.texto = texto

        db.session.commit()

        flash(
            "Aviso atualizado com sucesso!",
            "success"
        )

        return redirect(
            url_for("avisos.admin")
        )

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    return render_template(
        "aviso_form.html",
        aviso=aviso,
        titulo=aviso.titulo,
        texto=aviso.texto,
        editar=True
    )


# ============================================================
# INATIVAR AVISO
# ============================================================

@avisos_bp.route(
    "/<int:aviso_id>/inativar",
    methods=["POST"]
)
@login_required
def inativar(aviso_id):

    administrador_required()

    aviso = db.session.get(
        Aviso,
        aviso_id
    )

    if aviso is None:
        abort(404)

    # --------------------------------------------------------
    # VERIFICA SE JÁ ESTÁ INATIVO
    # --------------------------------------------------------

    if not aviso.ativo:

        flash(
            "Este aviso já está inativo.",
            "warning"
        )

        return redirect(
            url_for("avisos.admin")
        )

    # --------------------------------------------------------
    # INATIVA
    # --------------------------------------------------------

    aviso.ativo = False

    aviso.data_inativacao = datetime.utcnow()

    aviso.usuario_inativacao = current_user.id

    db.session.commit()

    flash(
        "Aviso inativado com sucesso!",
        "success"
    )

    return redirect(
        url_for("avisos.admin")
    )


# ============================================================
# REATIVAR AVISO
# ============================================================

@avisos_bp.route(
    "/<int:aviso_id>/reativar",
    methods=["POST"]
)
@login_required
def reativar(aviso_id):

    administrador_required()

    aviso = db.session.get(
        Aviso,
        aviso_id
    )

    if aviso is None:
        abort(404)

    # --------------------------------------------------------
    # VERIFICA SE JÁ ESTÁ ATIVO
    # --------------------------------------------------------

    if aviso.ativo:

        flash(
            "Este aviso já está ativo.",
            "warning"
        )

        return redirect(
            url_for("avisos.admin")
        )

    # --------------------------------------------------------
    # REATIVA
    # --------------------------------------------------------

    aviso.ativo = True

    # Mantemos o histórico da última inativação.
    # Não apagamos data_inativacao nem usuario_inativacao.

    db.session.commit()

    flash(
        "Aviso reativado com sucesso!",
        "success"
    )

    return redirect(
        url_for("avisos.admin")
    )