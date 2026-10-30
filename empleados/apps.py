from django.apps import AppConfig


class EmpleadosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "empleados"
    verbose_name = "Nómina"

    def ready(self):
        from . import signals  # noqa: F401
