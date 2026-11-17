
from django.db import models
from django.conf import settings
from django.utils import timezone

from .sla import adicionar_horas_uteis


class Chamado(models.Model):

    class Prioridade(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        MEDIA = "media", "Média"
        ALTA = "alta", "Alta"
        URGENTE = "urgente", "Urgente"

    class Status(models.TextChoices):
        ABERTO = "aberto", "Aberto"
        EM_ATENDIMENTO = "em_atendimento", "Em atendimento"
        AGUARDANDO_CLIENTE = "aguardando_cliente", "Aguardando cliente"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    PRAZOS_SLA = {
        "urgente": {"resposta": 30, "resolucao": 240},
        "alta": {"resposta": 60, "resolucao": 480},
        "media": {"resposta": 240, "resolucao": 960},
        "baixa": {"resposta": 480, "resolucao": 2400},
    }

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        related_name="chamados"
    )

    solicitante = models.CharField(max_length=150)
    email = models.EmailField(blank=True)

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()

    prioridade = models.CharField(
        max_length=10,
        choices=Prioridade.choices,
        default=Prioridade.MEDIA
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ABERTO
    )

    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chamados_atribuidos"
    )

    prazo_primeira_resposta = models.DateTimeField(
        null=True,
        blank=True
    )

    prazo_resolucao = models.DateTimeField(
        null=True,
        blank=True
    )

    primeira_resposta_em = models.DateTimeField(
        null=True,
        blank=True
    )

    resolvido_em = models.DateTimeField(
        null=True,
        blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.id} - {self.titulo}"

    def save(self, *args, **kwargs):
        usuario_acao = kwargs.pop("usuario_acao", None)

        novo_chamado = self.pk is None

        if novo_chamado:
            agora = timezone.now()
            prazos = self.PRAZOS_SLA[self.prioridade]

            self.prazo_primeira_resposta = adicionar_horas_uteis(
                agora, prazos["resposta"]
            )

            self.prazo_resolucao = adicionar_horas_uteis(
                agora, prazos["resolucao"]
            )

        else:
            anterior = Chamado.objects.filter(pk=self.pk).first()

            if anterior:
                if anterior.status != self.status:
                    HistoricoChamado.objects.create(
                        chamado=self,
                        usuario=usuario_acao,
                        tipo=HistoricoChamado.Tipo.STATUS,
                        descricao=(
                            f"Status alterado de "
                            f"'{anterior.get_status_display()}' para "
                            f"'{self.get_status_display()}'."
                        )
                    )

                    if (
                        self.status == self.Status.CONCLUIDO
                        and not anterior.resolvido_em
                    ):
                        self.resolvido_em = timezone.now()

                    elif (
                        anterior.status == self.Status.CONCLUIDO
                        and self.status != self.Status.CONCLUIDO
                    ):
                        self.resolvido_em = None

                if anterior.responsavel_id != self.responsavel_id:
                    nome_anterior = (
                        anterior.responsavel.username
                        if anterior.responsavel else "Nenhum"
                    )

                    nome_novo = (
                        self.responsavel.username
                        if self.responsavel else "Nenhum"
                    )

                    HistoricoChamado.objects.create(
                        chamado=self,
                        usuario=usuario_acao,
                        tipo=HistoricoChamado.Tipo.RESPONSAVEL,
                        descricao=(
                            f"Responsável alterado de "
                            f"'{nome_anterior}' para '{nome_novo}'."
                        )
                    )

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Chamado"
        verbose_name_plural = "Chamados"


class HistoricoChamado(models.Model):

    class Tipo(models.TextChoices):
        COMENTARIO = "comentario", "Comentário"
        STATUS = "status", "Alteração de status"
        RESPONSAVEL = "responsavel", "Alteração de responsável"
        SISTEMA = "sistema", "Registro do sistema"

    chamado = models.ForeignKey(
        Chamado,
        on_delete=models.CASCADE,
        related_name="historico"
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historicos_chamados"
    )

    tipo = models.CharField(
        max_length=15,
        choices=Tipo.choices,
        default=Tipo.COMENTARIO
    )

    descricao = models.TextField()

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]
        verbose_name = "Histórico do chamado"
        verbose_name_plural = "Históricos dos chamados"

    def __str__(self):
        return f"Histórico do chamado #{self.chamado_id}"
