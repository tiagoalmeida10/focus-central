
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Cliente
from .forms import ClienteForm


@login_required
def lista_clientes(request):
    busca = request.GET.get("busca", "").strip()

    clientes = Cliente.objects.all()

    if busca:
        clientes = clientes.filter(
            Q(nome__icontains=busca) |
            Q(documento__icontains=busca) |
            Q(email__icontains=busca)
        )

    contexto = {
        "clientes": clientes,
        "busca": busca,
    }

    return render(request, "clientes/lista_clientes.html", contexto)


@login_required
def formulario_cliente(request, cliente_id=None):
    if cliente_id:
        cliente = get_object_or_404(Cliente, pk=cliente_id)
    else:
        cliente = None

    form = ClienteForm(
        request.POST or None,
        instance=cliente
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("lista_clientes")

    return render(
        request,
        "clientes/formulario_cliente.html",
        {
            "form": form,
            "cliente": cliente,
        }
    )
