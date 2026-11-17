
from datetime import datetime, time, timedelta

from django.utils import timezone


HORA_INICIO = time(8, 0)
HORA_FIM = time(18, 0)


def adicionar_horas_uteis(data_inicio, minutos):
    """
    Adiciona minutos considerando apenas:
    - Segunda a sexta-feira
    - Das 08:00 às 18:00
    """

    atual = timezone.localtime(data_inicio)
    fuso = atual.tzinfo
    restante = minutos

    while restante > 0:

        # Pular sábado e domingo
        while atual.weekday() >= 5:
            proximo_dia = atual.date() + timedelta(days=1)
            atual = timezone.make_aware(
                datetime.combine(proximo_dia, HORA_INICIO),
                fuso
            )

        # Se estiver antes das 08h, começar às 08h
        if atual.time() < HORA_INICIO:
            atual = timezone.make_aware(
                datetime.combine(atual.date(), HORA_INICIO),
                fuso
            )

        # Se já passou das 18h, avançar para o próximo dia
        if atual.time() >= HORA_FIM:
            proximo_dia = atual.date() + timedelta(days=1)
            atual = timezone.make_aware(
                datetime.combine(proximo_dia, HORA_INICIO),
                fuso
            )
            continue

        # Calcular minutos disponíveis até as 18h
        fim_expediente = timezone.make_aware(
            datetime.combine(atual.date(), HORA_FIM),
            fuso
        )

        disponivel = int(
            (fim_expediente - atual).total_seconds() // 60
        )

        if restante <= disponivel:
            atual += timedelta(minutes=restante)
            restante = 0
        else:
            restante -= disponivel

            proximo_dia = atual.date() + timedelta(days=1)
            atual = timezone.make_aware(
                datetime.combine(proximo_dia, HORA_INICIO),
                fuso
            )

    return atual
