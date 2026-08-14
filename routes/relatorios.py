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
    login_required,
    current_user
)

from database.models import (
    db,
    Relatorio
)

from utils.turnos import (
    obter_turno,
    obter_horario_turno
)


# ============================================================
# BLUEPRINT
# ============================================================

relatorios_bp = Blueprint(
    "relatorios",
    __name__,
    url_prefix="/relatorios"
)


# ============================================================
# NOVO RELATÓRIO
# ============================================================

@relatorios_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():

    # ========================================================
    # DATA E TURNO ATUAL
    # ========================================================

    agora = datetime.now()

    data_atual = agora.strftime("%d/%m/%Y")

    turno_atual = obter_turno(agora)

    horario_turno = obter_horario_turno(
        turno_atual
    )


    # ========================================================
    # SALVAR
    # ========================================================

    if request.method == "POST":

        descricao = request.form.get(
            "descricao",
            ""
        ).strip()


        # ----------------------------------------------------
        # VALIDAÇÃO
        # ----------------------------------------------------

        if not descricao:

            flash(
                "A descrição do relatório é obrigatória.",
                "danger"
            )

            return render_template(
                "relatorios/novo.html",
                data_atual=data_atual,
                turno_atual=turno_atual,
                horario_turno=horario_turno,
                descricao=descricao
            )


        # ----------------------------------------------------
        # CRIA RELATÓRIO
        # ----------------------------------------------------

        relatorio = Relatorio(
            usuario_id=current_user.id,

            data_hora=agora,

            turno=turno_atual,

            descricao=descricao
        )

        db.session.add(relatorio)

        db.session.commit()


        # ----------------------------------------------------
        # MENSAGEM
        # ----------------------------------------------------

        flash(
            "Relatório registrado com sucesso.",
            "success"
        )


        # ----------------------------------------------------
        # REDIRECIONAMENTO
        # ----------------------------------------------------

        return redirect(
            url_for(
                "relatorios.visualizar",
                relatorio_id=relatorio.id
            )
        )


    # ========================================================
    # FORMULÁRIO
    # ========================================================

    return render_template(
        "relatorios/novo.html",

        data_atual=data_atual,

        turno_atual=turno_atual,

        horario_turno=horario_turno
    )


# ============================================================
# HISTÓRICO
# ============================================================

@relatorios_bp.route("/historico")
@login_required
def historico():

    relatorios = (
        db.session.scalars(
            db.select(Relatorio)
            .order_by(
                Relatorio.data_hora.desc()
            )
        )
        .all()
    )


    return render_template(
        "relatorios/historico.html",
        relatorios=relatorios
    )


# ============================================================
# VISUALIZAR RELATÓRIO
# ============================================================

@relatorios_bp.route(
    "/visualizar/<int:relatorio_id>"
)
@login_required
def visualizar(relatorio_id):

    relatorio = db.session.get(
        Relatorio,
        relatorio_id
    )


    # ========================================================
    # RELATÓRIO NÃO ENCONTRADO
    # ========================================================

    if relatorio is None:

        flash(
            "Relatório não encontrado.",
            "danger"
        )

        return redirect(
            url_for("relatorios.historico")
        )


    # ========================================================
    # VISUALIZAÇÃO
    # ========================================================

    return render_template(
        "relatorios/visualizar.html",
        relatorio=relatorio
    )


# ============================================================
# EDITAR RELATÓRIO
# ============================================================

@relatorios_bp.route(
    "/editar/<int:relatorio_id>",
    methods=["GET", "POST"]
)
@login_required
def editar(relatorio_id):

    relatorio = db.session.get(
        Relatorio,
        relatorio_id
    )


    # ========================================================
    # RELATÓRIO NÃO ENCONTRADO
    # ========================================================

    if relatorio is None:

        flash(
            "Relatório não encontrado.",
            "danger"
        )

        return redirect(
            url_for("relatorios.historico")
        )


    # ========================================================
    # VERIFICA AUTOR
    # ========================================================

    if relatorio.usuario_id != current_user.id:

        flash(
            "Você não tem permissão para editar este relatório.",
            "danger"
        )

        return redirect(
            url_for(
                "relatorios.visualizar",
                relatorio_id=relatorio.id
            )
        )


    # ========================================================
    # SALVAR ALTERAÇÕES
    # ========================================================

    if request.method == "POST":

        descricao = request.form.get(
            "descricao",
            ""
        ).strip()


        # ----------------------------------------------------
        # VALIDAÇÃO
        # ----------------------------------------------------

        if not descricao:

            flash(
                "A descrição do relatório é obrigatória.",
                "danger"
            )

            return render_template(
                "relatorios/editar.html",
                relatorio=relatorio
            )


        # ----------------------------------------------------
        # ALTERA SOMENTE A DESCRIÇÃO
        # ----------------------------------------------------

        relatorio.descricao = descricao


        # ----------------------------------------------------
        # SALVA
        # ----------------------------------------------------

        db.session.commit()


        # ----------------------------------------------------
        # MENSAGEM
        # ----------------------------------------------------

        flash(
            "Relatório atualizado com sucesso.",
            "success"
        )


        # ----------------------------------------------------
        # VOLTA PARA VISUALIZAÇÃO
        # ----------------------------------------------------

        return redirect(
            url_for(
                "relatorios.visualizar",
                relatorio_id=relatorio.id
            )
        )


    # ========================================================
    # FORMULÁRIO DE EDIÇÃO
    # ========================================================

    return render_template(
        "relatorios/editar.html",
        relatorio=relatorio
    )


# ============================================================
# EXCLUIR RELATÓRIO
# ============================================================

@relatorios_bp.route(
    "/excluir/<int:relatorio_id>",
    methods=["POST"]
)
@login_required
def excluir(relatorio_id):

    relatorio = db.session.get(
        Relatorio,
        relatorio_id
    )


    # ========================================================
    # RELATÓRIO NÃO ENCONTRADO
    # ========================================================

    if relatorio is None:

        flash(
            "Relatório não encontrado.",
            "danger"
        )

        return redirect(
            url_for("relatorios.historico")
        )


    # ========================================================
    # VERIFICA AUTOR
    # ========================================================

    if relatorio.usuario_id != current_user.id:

        flash(
            "Você não tem permissão para excluir este relatório.",
            "danger"
        )

        return redirect(
            url_for(
                "relatorios.visualizar",
                relatorio_id=relatorio.id
            )
        )


    # ========================================================
    # EXCLUI
    # ========================================================

    db.session.delete(relatorio)

    db.session.commit()


    # ========================================================
    # MENSAGEM
    # ========================================================

    flash(
        "Relatório excluído com sucesso.",
        "success"
    )


    # ========================================================
    # VOLTA PARA HISTÓRICO
    # ========================================================

    return redirect(
        url_for("relatorios.historico")
    )