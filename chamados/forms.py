
from django import forms
from .models import Chamado, HistoricoChamado


class ChamadoForm(forms.ModelForm):

    class Meta:
        model = Chamado
        fields = [
            "cliente",
            "solicitante",
            "email",
            "titulo",
            "descricao",
            "prioridade",
        ]

        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "solicitante": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "titulo": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
            }),
            "prioridade": forms.Select(attrs={"class": "form-select"}),
        }


class ChamadoAtualizacaoForm(forms.ModelForm):

    class Meta:
        model = Chamado
        fields = ["status", "responsavel"]

        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "responsavel": forms.Select(attrs={"class": "form-select"}),
        }


class ComentarioChamadoForm(forms.Form):

    descricao = forms.CharField(
        label="Comentário",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Digite seu comentário ou atualização...",
        })
    )
