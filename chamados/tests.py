
from datetime import datetime

from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

from .sla import adicionar_horas_uteis
from .models import Chamado, HistoricoChamado
from clientes.models import Cliente


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


class TesteFuncionalidadesChamados(TestCase):

    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="usuario_teste",
            password="senha_teste_123"
        )

        self.cliente = Cliente.objects.create(
            nome="Cliente Teste",
            documento="12345678000199",
            email="cliente@teste.com",
            telefone="41999999999"
        )

        self.client.login(
            username="usuario_teste",
            password="senha_teste_123"
        )

    def criar_chamado(self):
        return Chamado.objects.create(
            cliente=self.cliente,
            solicitante="Solicitante Teste",
            email="solicitante@teste.com",
            titulo="Chamado de teste",
            descricao="Descrição do chamado de teste",
            prioridade=Chamado.Prioridade.MEDIA
        )

    def test_abertura_de_chamado(self):
        resposta = self.client.post(
            reverse("novo_chamado"),
            {
                "cliente": self.cliente.id,
                "solicitante": "Solicitante Teste",
                "email": "solicitante@teste.com",
                "titulo": "Problema de conexão",
                "descricao": "Teste de abertura de chamado",
                "prioridade": "media",
            }
        )

        self.assertEqual(resposta.status_code, 200)

        chamado = Chamado.objects.get(
            titulo="Problema de conexão"
        )

        self.assertEqual(chamado.status, Chamado.Status.ABERTO)
        self.assertIsNotNone(chamado.prazo_primeira_resposta)
        self.assertIsNotNone(chamado.prazo_resolucao)

    def test_atualizacao_de_status_e_responsavel(self):
        chamado = self.criar_chamado()

        resposta = self.client.post(
            reverse("detalhe_chamado", args=[chamado.id]),
            {
                "acao": "atualizar",
                "status": Chamado.Status.EM_ATENDIMENTO,
                "responsavel": self.usuario.id,
            }
        )

        self.assertEqual(resposta.status_code, 302)

        chamado.refresh_from_db()

        self.assertEqual(
            chamado.status,
            Chamado.Status.EM_ATENDIMENTO
        )

        self.assertEqual(
            chamado.responsavel,
            self.usuario
        )

        self.assertEqual(
            HistoricoChamado.objects.filter(chamado=chamado).count(),
            2
        )

    def test_registro_de_comentario(self):
        chamado = self.criar_chamado()

        resposta = self.client.post(
            reverse("detalhe_chamado", args=[chamado.id]),
            {
                "acao": "comentar",
                "descricao": "Comentário de teste do chamado",
            }
        )

        self.assertEqual(resposta.status_code, 302)

        historico = HistoricoChamado.objects.get(
            chamado=chamado,
            tipo=HistoricoChamado.Tipo.COMENTARIO
        )

        self.assertEqual(
            historico.descricao,
            "Comentário de teste do chamado"
        )

        chamado.refresh_from_db()

        self.assertIsNotNone(chamado.primeira_resposta_em)
