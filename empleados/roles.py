from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

ADMIN = "admin"
PERSONAL = "personal"
GERENCIA = "gerencia"


def rol_de(user):
    """Devuelve el rol del usuario. Superusuario siempre es admin."""
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return ADMIN
    perfil = getattr(user, "perfil", None)
    return perfil.rol if perfil else PERSONAL


def etiqueta_rol(user):
    from .models import Perfil

    etiquetas = dict(Perfil.Rol.choices)
    return etiquetas.get(rol_de(user), "")


def roles_requeridos(*roles):
    """Restringe una vista a los roles indicados."""

    def decorador(view):
        @wraps(view)
        @login_required
        def envoltorio(request, *args, **kwargs):
            if rol_de(request.user) not in roles:
                messages.error(
                    request, "No tienes permisos para realizar esta acción."
                )
                return redirect("empleado_lista")
            return view(request, *args, **kwargs)

        return envoltorio

    return decorador
