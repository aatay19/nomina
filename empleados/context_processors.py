from .roles import etiqueta_rol, rol_de


def rol_usuario(request):
    return {
        "user_rol": rol_de(request.user),
        "user_rol_label": etiqueta_rol(request.user),
    }
