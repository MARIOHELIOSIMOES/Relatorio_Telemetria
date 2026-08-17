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
# QUALQUER USUÁRIO AUTENTICADO
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
# GERENCIAMENTO DE AVISOS
# QUALQUER USUÁRIO AUTENTICADO
# MOSTRA ATIVOS E INATIVOS
# ============================================================

@avisos_bp.route("/admin")
@login_required
def admin():

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
# QUALQUER USUÁRIO AUTENTICADO
# ============================================================

@avisos_bp.route(
    "/novo",
    methods=["GET", "POST"]
)
@login_required
def novo():

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
        # VALIDAÇÃO DO TÍTULO
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


        # ----------------------------------------------------
        # VALIDAÇÃO DO TEXTO
        # ----------------------------------------------------

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
            data_criacao=datetime.now(),
            ativo=True
        )

        db.session.add(aviso)

        db.session.commit()


        # ----------------------------------------------------
        # MENSAGEM
        # ----------------------------------------------------

        flash(
            "Aviso publicado com sucesso!",
            "success"
        )


        # ----------------------------------------------------
        # REDIRECIONAMENTO
        # ----------------------------------------------------

        return redirect(
            url_for("avisos.admin")
        )


    # ========================================================
    # FORMULÁRIO
    # ========================================================

    return render_template(
        "aviso_form.html",
        titulo="",
        texto=""
    )


# ============================================================
# EDITAR AVISO
# QUALQUER USUÁRIO AUTENTICADO
# ============================================================

@avisos_bp.route(
    "/<int:aviso_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar(aviso_id):

    aviso = db.session.get(
        Aviso,
        aviso_id
    )


    # ========================================================
    # AVISO NÃO ENCONTRADO
    # ========================================================

    if aviso is None:

        abort(404)


    # ========================================================
    # FORMULÁRIO
    # ========================================================

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
        # VALIDAÇÃO DO TÍTULO
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


        # ----------------------------------------------------
        # VALIDAÇÃO DO TEXTO
        # ----------------------------------------------------

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
        # ATUALIZA AVISO
        # ----------------------------------------------------

        aviso.titulo = titulo
        aviso.texto = texto

        db.session.commit()


        # ----------------------------------------------------
        # MENSAGEM
        # ----------------------------------------------------

        flash(
            "Aviso atualizado com sucesso!",
            "success"
        )


        # ----------------------------------------------------
        # REDIRECIONAMENTO
        # ----------------------------------------------------

        return redirect(
            url_for("avisos.admin")
        )


    # ========================================================
    # GET
    # ========================================================

    return render_template(
        "aviso_form.html",
        aviso=aviso,
        titulo=aviso.titulo,
        texto=aviso.texto,
        editar=True
    )


# ============================================================
# INATIVAR AVISO
# QUALQUER USUÁRIO AUTENTICADO
# ============================================================

@avisos_bp.route(
    "/<int:aviso_id>/inativar",
    methods=["POST"]
)
@login_required
def inativar(aviso_id):

    aviso = db.session.get(
        Aviso,
        aviso_id
    )


    # ========================================================
    # AVISO NÃO ENCONTRADO
    # ========================================================

    if aviso is None:

        abort(404)


    # ========================================================
    # VERIFICA SE JÁ ESTÁ INATIVO
    # ========================================================

    if not aviso.ativo:

        flash(
            "Este aviso já está inativo.",
            "warning"
        )

        return redirect(
            url_for("avisos.admin")
        )


    # ========================================================
    # INATIVA
    # ========================================================

    aviso.ativo = False

    aviso.data_inativacao = datetime.now()

    aviso.usuario_inativacao = current_user.id

    db.session.commit()


    # ========================================================
    # MENSAGEM
    # ========================================================

    flash(
        "Aviso inativado com sucesso!",
        "success"
    )


    # ========================================================
    # REDIRECIONAMENTO
    # ========================================================

    return redirect(
        url_for("avisos.admin")
    )


# ============================================================
# REATIVAR AVISO
# QUALQUER USUÁRIO AUTENTICADO
# ============================================================

@avisos_bp.route(
    "/<int:aviso_id>/reativar",
    methods=["POST"]
)
@login_required
def reativar(aviso_id):

    aviso = db.session.get(
        Aviso,
        aviso_id
    )


    # ========================================================
    # AVISO NÃO ENCONTRADO
    # ========================================================

    if aviso is None:

        abort(404)


    # ========================================================
    # VERIFICA SE JÁ ESTÁ ATIVO
    # ========================================================

    if aviso.ativo:

        flash(
            "Este aviso já está ativo.",
            "warning"
        )

        return redirect(
            url_for("avisos.admin")
        )


    # ========================================================
    # REATIVA
    # ========================================================

    aviso.ativo = True

    # Mantemos o histórico da última inativação.
    # Não apagamos data_inativacao nem usuario_inativacao.

    db.session.commit()


    # ========================================================
    # MENSAGEM
    # ========================================================

    flash(
        "Aviso reativado com sucesso!",
        "success"
    )


    # ========================================================
    # REDIRECIONAMENTO
    # ========================================================

    return redirect(
        url_for("avisos.admin")
    )


# ============================================================
# EXCLUIR AVISO
# SOMENTE ADMINISTRADOR
# ============================================================

@avisos_bp.route(
    "/<int:aviso_id>/excluir",
    methods=["POST"]
)
@login_required
def excluir(aviso_id):

    # ========================================================
    # VERIFICA ADMINISTRADOR
    # ========================================================

    administrador_required()


    # ========================================================
    # LOCALIZA AVISO
    # ========================================================

    aviso = db.session.get(
        Aviso,
        aviso_id
    )


    # ========================================================
    # AVISO NÃO ENCONTRADO
    # ========================================================

    if aviso is None:

        flash(
            "Aviso não encontrado.",
            "danger"
        )

        return redirect(
            url_for("avisos.admin")
        )


    # ========================================================
    # EXCLUSÃO DEFINITIVA
    # ========================================================

    db.session.delete(aviso)

    db.session.commit()


    # ========================================================
    # MENSAGEM
    # ========================================================

    flash(
        "Aviso excluído definitivamente.",
        "success"
    )


    # ========================================================
    # REDIRECIONAMENTO
    # ========================================================

    return redirect(
        url_for("avisos.admin")
    )