
from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("chamados/", views.lista_chamados, name="lista_chamados"),
    path("chamados/novo/", views.novo_chamado, name="novo_chamado"),
    path(
        "chamados/<int:chamado_id>/",
        views.detalhe_chamado,
        name="detalhe_chamado"
    ),
]
