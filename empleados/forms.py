import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Empleado, HorasTrabajo, Perfil

INPUT = "form-input"


def aplicar_estilos(form, omitir=("activo",)):
    for name, field in form.fields.items():
        if name in omitir:
            continue
        if isinstance(field.widget, forms.CheckboxInput):
            css = "form-check"
        else:
            css = INPUT
        existing = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = f"{existing} {css}".strip()


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            "cedula",
            "nombre",
            "apellido",
            "sexo",
            "fecha_nacimiento",
            "cargo",
            "departamento",
            "tipo_contrato",
            "fecha_ingreso",
            "fecha_egreso",
            "salario",
            "salario_minimo",
            "email",
            "telefono",
            "direccion",
            "vehiculo",
            "tiene_licencia",
            "grado_licencia",
            "activo",
            "notas",
        ]
        widgets = {
            "cedula": forms.TextInput(attrs={"placeholder": "V-12345678"}),
            "nombre": forms.TextInput(attrs={"placeholder": "Nombre"}),
            "apellido": forms.TextInput(attrs={"placeholder": "Apellido"}),
            "email": forms.EmailInput(attrs={"placeholder": "correo@ejemplo.com"}),
            "telefono": forms.TextInput(attrs={"placeholder": "0412-0000000"}),
            "cargo": forms.TextInput(attrs={"placeholder": "Cargo"}),
            "departamento": forms.TextInput(attrs={"placeholder": "Departamento"}),
            "direccion": forms.TextInput(attrs={"placeholder": "Dirección"}),
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
            "fecha_ingreso": forms.DateInput(attrs={"type": "date"}),
            "fecha_egreso": forms.DateInput(attrs={"type": "date"}),
            "salario": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "salario_minimo": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "notas": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_estilos(self)


class HorasTrabajoForm(forms.ModelForm):
    class Meta:
        model = HorasTrabajo
        fields = ["empleado", "fecha", "horas", "horas_extra", "descripcion"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "horas": forms.NumberInput(attrs={"step": "0.5", "min": "0"}),
            "horas_extra": forms.NumberInput(attrs={"step": "0.5", "min": "0"}),
            "descripcion": forms.TextInput(
                attrs={"placeholder": "Descripción del trabajo realizado"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["empleado"].queryset = Empleado.objects.all()
        self.fields["empleado"].empty_label = "Selecciona un empleado"
        if not self.is_bound and not self.initial.get("fecha"):
            self.initial["fecha"] = datetime.date.today()
        aplicar_estilos(self)


class UsuarioCrearForm(UserCreationForm):
    rol = forms.ChoiceField(
        choices=Perfil.Rol.choices,
        label="Rol",
        initial=Perfil.Rol.PERSONAL,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels = {
            "username": "Usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "usuario"
        self.fields["first_name"].widget.attrs["placeholder"] = "Nombre"
        self.fields["last_name"].widget.attrs["placeholder"] = "Apellido"
        self.fields["email"].widget.attrs["placeholder"] = "correo@ejemplo.com"
        aplicar_estilos(self, omitir=())

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Perfil.objects.update_or_create(
                usuario=user, defaults={"rol": self.cleaned_data["rol"]}
            )
        return user


class UsuarioEditarForm(forms.ModelForm):
    rol = forms.ChoiceField(choices=Perfil.Rol.choices, label="Rol")
    nueva_password = forms.CharField(
        required=False,
        label="Nueva contraseña",
        widget=forms.PasswordInput(render_value=False),
        help_text="Déjala vacía para conservar la contraseña actual.",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active")
        labels = {
            "username": "Usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "is_active": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            perfil = getattr(self.instance, "perfil", None)
            self.fields["rol"].initial = (
                perfil.rol if perfil else Perfil.Rol.PERSONAL
            )
        aplicar_estilos(self, omitir=("is_active",))

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Perfil.objects.update_or_create(
                usuario=user, defaults={"rol": self.cleaned_data["rol"]}
            )
            nueva = self.cleaned_data.get("nueva_password")
            if nueva:
                user.set_password(nueva)
                user.save(update_fields=["password"])
        return user
