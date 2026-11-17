
from datetime import datetime

from django.test import SimpleTestCase
from django.utils import timezone

from .sla import adicionar_horas_uteis


class TesteSLA(SimpleTestCase):

    def criar_data(self, ano, mes, dia, hora, minuto=0):
        data = datetime(ano, mes, dia, hora, minuto)
        return timezone.make_aware(data)

    def test_sla_dentro_do_expediente(self):
        inicio = self.criar_data(2026, 11, 17, 9)
        resultado = adicionar_horas_uteis(inicio, 60)

        self.assertEqual(resultado.hour, 10)
        self.assertEqual(resultado.minute, 0)

    def test_sla_ultrapassa_expediente(self):
        inicio = self.criar_data(2026, 11, 17, 17)
        resultado = adicionar_horas_uteis(inicio, 120)

        self.assertEqual(resultado.weekday(), 2)
        self.assertEqual(resultado.hour, 9)

    def test_sla_pula_final_de_semana(self):
        inicio = self.criar_data(2026, 11, 20, 17)
        resultado = adicionar_horas_uteis(inicio, 120)

        self.assertEqual(resultado.weekday(), 0)
        self.assertEqual(resultado.hour, 9)
