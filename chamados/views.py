
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Chamado, HistoricoChamado
from .forms import (
    ChamadoForm,
    ChamadoAtualizacaoForm,
    ComentarioChamadoForm,
)
from .sla import adicionar_horas_uteis


def avaliar_sla(prazo, data_conclusao=None):
    if not prazo:
        return "sem_prazo"

    if data_conclusao:
        return "cumprido" if data_conclusao <= prazo else "vencido"

    agora = timezone.now()

    if agora > prazo:
        return "vencido"

    limite_proximo = adicionar_horas_uteis(agora, 30)

    if prazo <= limite_proximo:
        return "proximo"

    return "dentro"


@login_required
def dashboard(request):
    chamados = Chamado.objects.select_related("cliente", "responsavel")

    total_chamados = chamados.count()
    abertos = chamados.filter(status=Chamado.Status.ABERTO).count()
    em_atendimento = chamados.filter(
        status=Chamado.Status.EM_ATENDIMENTO
    ).count()
    aguardando_cliente = chamados.filter(
        status=Chamado.Status.AGUARDANDO_CLIENTE
    ).count()
    concluidos = chamados.filter(
        status=Chamado.Status.CONCLUIDO
    ).count()
    cancelados = chamados.filter(
        status=Chamado.Status.CANCELADO
    ).count()

    sla_vencidos = 0
    sla_proximos = 0
    sla_dentro = 0

    chamados_ativos = chamados.exclude(
        status__in=[
            Chamado.Status.CONCLUIDO,
            Chamado.Status.CANCELADO,
        ]
    )

    for chamado in chamados_ativos:
        primeira_resposta = avaliar_sla(
            chamado.prazo_primeira_resposta,
            chamado.primeira_resposta_em
        )
        resolucao = avaliar_sla(
            chamado.prazo_resolucao,
            chamado.resolvido_em
        )

        situacoes = [primeira_resposta, resolucao]

        if "vencido" in situacoes:
            sla_vencidos += 1
        elif "proximo" in situacoes:
            sla_proximos += 1
        elif "dentro" in situacoes:
            sla_dentro += 1

    chamados_recentes = chamados.order_by("-criado_em")[:10]

    contexto = {
        "total_chamados": total_chamados,
        "abertos": abertos,
        "em_atendimento": em_atendimento,
        "aguardando_cliente": aguardando_cliente,
        "concluidos": concluidos,
        "cancelados": cancelados,
        "sla_vencidos": sla_vencidos,
        "sla_proximos": sla_proximos,
        "sla_dentro": sla_dentro,
        "chamados_recentes": chamados_recentes,
    }

    return render(request, "chamados/dashboard.html", contexto)


@login_required
def lista_chamados(request):
    chamados = Chamado.objects.select_related(
        "cliente", "responsavel"
    ).all()

    status = request.GET.get("status", "")
    prioridade = request.GET.get("prioridade", "")

    if status:
        chamados = chamados.filter(status=status)

    if prioridade:
        chamados = chamados.filter(prioridade=prioridade)

    contexto = {
        "chamados": chamados,
        "status_selecionado": status,
        "prioridade_selecionada": prioridade,
        "opcoes_status": Chamado.Status.choices,
        "opcoes_prioridade": Chamado.Prioridade.choices,
    }

    return render(request, "chamados/lista_chamados.html", contexto)


@login_required
def novo_chamado(request):
    form = ChamadoForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        chamado = form.save(commit=False)
        chamado.save(usuario_acao=request.user)

        return render(
            request,
            "chamados/sucesso_chamado.html",
            {"chamado": chamado}
        )

    return render(
        request,
        "chamados/novo_chamado.html",
        {"form": form}
    )


@login_required
def detalhe_chamado(request, chamado_id):
    chamado = get_object_or_404(
        Chamado.objects.select_related("cliente", "responsavel"),
        pk=chamado_id
    )

    atualizacao_form = ChamadoAtualizacaoForm(instance=chamado)
    comentario_form = ComentarioChamadoForm()

    if request.method == "POST":
        acao = request.POST.get("acao")

        if acao == "atualizar":
            atualizacao_form = ChamadoAtualizacaoForm(
                request.POST,
                instance=chamado
            )

            if atualizacao_form.is_valid():
                chamado_atualizado = atualizacao_form.save(commit=False)
                chamado_atualizado.save(usuario_acao=request.user)

                return redirect(
                    "detalhe_chamado",
                    chamado_id=chamado.id
                )

        elif acao == "comentar":
            comentario_form = ComentarioChamadoForm(request.POST)

            if comentario_form.is_valid():
                descricao = comentario_form.cleaned_data["descricao"]

                HistoricoChamado.objects.create(
                    chamado=chamado,
                    usuario=request.user,
                    tipo=HistoricoChamado.Tipo.COMENTARIO,
                    descricao=descricao
                )

                if not chamado.primeira_resposta_em:
                    chamado.primeira_resposta_em = timezone.now()
                    chamado.save(
                        update_fields=["primeira_resposta_em"]
                    )

                return redirect(
                    "detalhe_chamado",
                    chamado_id=chamado.id
                )

    historico = chamado.historico.select_related("usuario").all()

    sla_primeira_resposta = avaliar_sla(
        chamado.prazo_primeira_resposta,
        chamado.primeira_resposta_em
    )

    if chamado.status == Chamado.Status.CANCELADO:
        sla_resolucao = "cancelado"
    else:
        sla_resolucao = avaliar_sla(
            chamado.prazo_resolucao,
            chamado.resolvido_em
        )

    contexto = {
        "chamado": chamado,
        "historico": historico,
        "atualizacao_form": atualizacao_form,
        "comentario_form": comentario_form,
        "sla_primeira_resposta": sla_primeira_resposta,
        "sla_resolucao": sla_resolucao,
    }

    return render(
        request,
        "chamados/detalhe_chamado.html",
        contexto
    )
