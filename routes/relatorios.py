from datetime import datetime, timedelta

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
    Relatorio,
    Usuario
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

    # ========================================================
    # DATAS PADRÃO
    # ========================================================

    hoje = datetime.now().date()

    ontem = hoje - timedelta(days=1)


    # ========================================================
    # RECEBE FILTROS
    # ========================================================

    data_inicio = request.args.get(
        "data_inicio",
        ""
    ).strip()

    data_fim = request.args.get(
        "data_fim",
        ""
    ).strip()

    turno = request.args.get(
        "turno",
        ""
    ).strip()

    usuario_id = request.args.get(
        "usuario_id",
        ""
    ).strip()


    # ========================================================
    # SE NÃO INFORMOU DATA, USA ONTEM E HOJE
    # ========================================================

    if not data_inicio:

        data_inicio = ontem.strftime(
            "%Y-%m-%d"
        )


    if not data_fim:

        data_fim = hoje.strftime(
            "%Y-%m-%d"
        )


    # ========================================================
    # CONVERTE DATAS
    # ========================================================

    try:

        data_inicio_obj = datetime.strptime(
            data_inicio,
            "%Y-%m-%d"
        )

        data_fim_obj = datetime.strptime(
            data_fim,
            "%Y-%m-%d"
        )

        # ----------------------------------------------------
        # O dia final deve ser incluído integralmente.
        #
        # Exemplo:
        #
        # Data final = 14/08/2026
        #
        # Consulta:
        # < 15/08/2026 00:00:00
        #
        # Dessa forma, registros feitos durante todo
        # o dia 14/08 são incluídos.
        # ----------------------------------------------------

        data_fim_exclusiva = (
            data_fim_obj + timedelta(days=1)
        )

    except ValueError:

        flash(
            "Período de datas inválido.",
            "danger"
        )

        data_inicio = ontem.strftime(
            "%Y-%m-%d"
        )

        data_fim = hoje.strftime(
            "%Y-%m-%d"
        )

        data_inicio_obj = datetime.combine(
            ontem,
            datetime.min.time()
        )

        data_fim_exclusiva = datetime.combine(
            hoje + timedelta(days=1),
            datetime.min.time()
        )


    # ========================================================
    # CONSULTA BASE
    # ========================================================

    query = db.select(
        Relatorio
    )


    # ========================================================
    # FILTRO POR PERÍODO
    # ========================================================

    query = query.where(
        Relatorio.data_hora >= data_inicio_obj,
        Relatorio.data_hora < data_fim_exclusiva
    )


    # ========================================================
    # FILTRO POR TURNO
    # ========================================================

    if turno:

        query = query.where(
            Relatorio.turno == turno
        )


    # ========================================================
    # FILTRO POR USUÁRIO
    # ========================================================

    if usuario_id:

        try:

            usuario_id_int = int(
                usuario_id
            )

            query = query.where(
                Relatorio.usuario_id == usuario_id_int
            )

        except ValueError:

            usuario_id = ""


    # ========================================================
    # ORDENAÇÃO
    # ========================================================

    query = query.order_by(
        Relatorio.data_hora.desc()
    )


    # ========================================================
    # EXECUTA CONSULTA
    # ========================================================

    relatorios = db.session.scalars(
        query
    ).all()


    # ========================================================
    # USUÁRIOS PARA O FILTRO
    # ========================================================

    usuarios = (
        db.session.query(
            Usuario
        )
        .filter_by(
            ativo=True
        )
        .order_by(
            Usuario.nome.asc()
        )
        .all()
    )


    # ========================================================
    # RENDERIZA
    # ========================================================

    return render_template(
        "relatorios/historico.html",

        relatorios=relatorios,

        usuarios=usuarios,

        data_inicio=data_inicio,

        data_fim=data_fim,

        turno=turno,

        usuario_id=usuario_id
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
            url_for(
                "relatorios.historico"
            )
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
            url_for(
                "relatorios.historico"
            )
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
            url_for(
                "relatorios.historico"
            )
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

    db.session.delete(
        relatorio
    )

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
        url_for(
            "relatorios.historico"
        )
    )