
from django.urls import path
from . import views

urlpatterns = [
    path("clientes/", views.lista_clientes, name="lista_clientes"),
    path("clientes/novo/", views.formulario_cliente, name="novo_cliente"),
    path(
        "clientes/<int:cliente_id>/editar/",
        views.formulario_cliente,
        name="editar_cliente"
    ),
]
