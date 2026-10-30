from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Empleado, HorasTrabajo, Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = "Rol"


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "mostrar_rol",
        "is_staff",
    )
    list_filter = ("perfil__rol", "is_staff", "is_superuser", "is_active")

    @admin.display(description="Rol")
    def mostrar_rol(self, obj):
        perfil = getattr(obj, "perfil", None)
        return perfil.get_rol_display() if perfil else "—"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol")
    list_filter = ("rol",)
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name")


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = (
        "cedula",
        "nombre",
        "apellido",
        "cargo",
        "tipo_contrato",
        "vehiculo",
        "tiene_licencia",
        "salario",
        "activo",
    )
    list_filter = (
        "activo",
        "departamento",
        "tipo_contrato",
        "sexo",
        "vehiculo",
        "tiene_licencia",
    )
    search_fields = ("cedula", "nombre", "apellido", "cargo")
    list_editable = ("activo",)


@admin.register(HorasTrabajo)
class HorasTrabajoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha", "horas", "horas_extra", "total_horas")
    list_filter = ("fecha",)
    search_fields = ("empleado__cedula", "empleado__nombre", "empleado__apellido")
    date_hierarchy = "fecha"
