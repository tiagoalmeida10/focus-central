
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Chamado, HistoricoChamado
from .sla import adicionar_horas_uteis


def avaliar_sla(prazo, data_conclusao=None):
    if not prazo:
        return "sem_prazo"

    if data_conclusao:
        if data_conclusao <= prazo:
            return "cumprido"
        return "vencido"

    agora = timezone.now()

    if agora > prazo:
        return "vencido"

    limite_proximo = adicionar_horas_uteis(agora, 30)

    if prazo <= limite_proximo:
        return "proximo"

    return "dentro"


def exibir_sla(situacao):
    estilos = {
        "cumprido": ("Cumprido", "#198754"),
        "dentro": ("Dentro do prazo", "#198754"),
        "proximo": ("Próximo do vencimento", "#d99a00"),
        "vencido": ("Vencido", "#dc3545"),
        "sem_prazo": ("Sem prazo", "#6c757d"),
        "cancelado": ("Cancelado", "#6c757d"),
    }

    texto, cor = estilos.get(
        situacao,
        ("Indefinido", "#6c757d")
    )

    return format_html(
        '<strong style="color: {};">{}</strong>',
        cor,
        texto
    )


class SlaFilter(admin.SimpleListFilter):
    title = "Situação do SLA"
    parameter_name = "situacao_sla"

    campo_prazo = None
    campo_conclusao = None
    campo_status = None

    def lookups(self, request, model_admin):
        return (
            ("cumprido", "Cumprido"),
            ("dentro", "Dentro do prazo"),
            ("proximo", "Próximo do vencimento"),
            ("vencido", "Vencido"),
            ("sem_prazo", "Sem prazo"),
        )

    def queryset(self, request, queryset):
        valor = self.value()

        if not valor:
            return queryset

        campos = [
            "id",
            self.campo_prazo,
            self.campo_conclusao,
        ]

        if self.campo_status:
            campos.append(self.campo_status)

        ids = []

        for chamado in queryset.only(*campos).iterator():

            if (
                self.campo_status
                and getattr(chamado, self.campo_status)
                == Chamado.Status.CANCELADO
            ):
                situacao = "cancelado"
            else:
                situacao = avaliar_sla(
                    getattr(chamado, self.campo_prazo),
                    getattr(chamado, self.campo_conclusao)
                )

            if situacao == valor:
                ids.append(chamado.pk)

        return queryset.filter(pk__in=ids)


class SlaPrimeiraRespostaFilter(SlaFilter):
    title = "SLA primeira resposta"
    parameter_name = "sla_primeira_resposta"
    campo_prazo = "prazo_primeira_resposta"
    campo_conclusao = "primeira_resposta_em"


class SlaResolucaoFilter(SlaFilter):
    title = "SLA resolução"
    parameter_name = "sla_resolucao"
    campo_prazo = "prazo_resolucao"
    campo_conclusao = "resolvido_em"
    campo_status = "status"


class HistoricoChamadoInline(admin.TabularInline):
    model = HistoricoChamado
    extra = 1

    readonly_fields = ("criado_em", "usuario")

    fields = (
        "tipo",
        "descricao",
        "usuario",
        "criado_em",
    )


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "titulo",
        "cliente",
        "prioridade",
        "status",
        "responsavel",
        "situacao_primeira_resposta",
        "situacao_resolucao",
        "prazo_primeira_resposta",
        "prazo_resolucao",
        "criado_em",
    )

    list_filter = (
        "status",
        "prioridade",
        SlaPrimeiraRespostaFilter,
        SlaResolucaoFilter,
        "criado_em",
    )

    search_fields = (
        "titulo",
        "descricao",
        "cliente__nome",
        "solicitante",
        "email",
    )

    ordering = ("-criado_em",)

    readonly_fields = (
        "criado_em",
        "atualizado_em",
        "prazo_primeira_resposta",
        "prazo_resolucao",
        "primeira_resposta_em",
        "resolvido_em",
    )

    inlines = [HistoricoChamadoInline]

    @admin.display(description="SLA primeira resposta")
    def situacao_primeira_resposta(self, obj):
        situacao = avaliar_sla(
            obj.prazo_primeira_resposta,
            obj.primeira_resposta_em
        )
        return exibir_sla(situacao)

    @admin.display(description="SLA resolução")
    def situacao_resolucao(self, obj):
        if obj.status == Chamado.Status.CANCELADO:
            return exibir_sla("cancelado")

        situacao = avaliar_sla(
            obj.prazo_resolucao,
            obj.resolvido_em
        )
        return exibir_sla(situacao)

    def save_model(self, request, obj, form, change):
        obj.save(usuario_acao=request.user)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.delete()

        for obj in instances:
            if not obj.usuario_id:
                obj.usuario = request.user

            obj.save()

            if (
                obj.tipo == HistoricoChamado.Tipo.COMENTARIO
                and not form.instance.primeira_resposta_em
            ):
                momento_resposta = timezone.now()

                Chamado.objects.filter(
                    pk=form.instance.pk,
                    primeira_resposta_em__isnull=True
                ).update(
                    primeira_resposta_em=momento_resposta
                )

                form.instance.primeira_resposta_em = momento_resposta

        formset.save_m2m()
