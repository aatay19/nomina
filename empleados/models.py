from django.conf import settings
from django.db import models
from django.urls import reverse


class Perfil(models.Model):
    class Rol(models.TextChoices):
        ADMIN = "admin", "Administrador"
        PERSONAL = "personal", "Personal"
        GERENCIA = "gerencia", "Gerencia"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Usuario",
    )
    rol = models.CharField(
        "Rol", max_length=20, choices=Rol.choices, default=Rol.PERSONAL
    )

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"{self.usuario} - {self.get_rol_display()}"


class Empleado(models.Model):
    class Sexo(models.TextChoices):
        MASCULINO = "M", "Masculino"
        FEMENINO = "F", "Femenino"
        OTRO = "O", "Otro"

    class TipoContrato(models.TextChoices):
        INDEFINIDO = "indefinido", "Indefinido"
        FIJO = "fijo", "Tiempo determinado"
        OBRA = "obra", "Por obra o labor"
        PASANTIA = "pasantia", "Pasantía"
        EVENTUAL = "eventual", "Eventual"

    class Vehiculo(models.TextChoices):
        CARRO = "carro", "Carro"
        MOTO = "moto", "Moto"
        NINGUNO = "ninguno", "Ninguno"

    class GradoLicencia(models.TextChoices):
        A = "A", "A (Motocicletas)"
        B = "B", "B (Automóviles)"
        C = "C", "C (Vehículos de carga)"
        D = "D", "D (Transporte público)"
        E = "E", "E (Articulados)"

    cedula = models.CharField("Código / Cédula", max_length=20, unique=True)
    nombre = models.CharField("Nombre completo", max_length=100)
    apellido = models.CharField("Apellido completo", max_length=100)

    cargo = models.CharField("Cargo", max_length=100, blank=True)
    departamento = models.CharField("Departamento", max_length=100, blank=True)
    tipo_contrato = models.CharField(
        "Tipo de contrato",
        max_length=20,
        choices=TipoContrato.choices,
        blank=True,
    )
    sexo = models.CharField(
        "Sexo", max_length=1, choices=Sexo.choices, blank=True
    )

    fecha_nacimiento = models.DateField("Fecha de nacimiento", null=True, blank=True)
    fecha_ingreso = models.DateField("Fecha de ingreso", null=True, blank=True)
    fecha_egreso = models.DateField("Fecha de egreso", null=True, blank=True)

    salario = models.DecimalField(
        "Salario", max_digits=12, decimal_places=2, null=True, blank=True
    )
    salario_minimo = models.DecimalField(
        "Salario mínimo", max_digits=12, decimal_places=2, null=True, blank=True
    )

    email = models.EmailField("Correo electrónico", blank=True)
    telefono = models.CharField("Teléfono", max_length=30, blank=True)
    direccion = models.CharField("Dirección", max_length=200, blank=True)
    vehiculo = models.CharField(
        "Vehículo", max_length=10, choices=Vehiculo.choices, blank=True
    )
    tiene_licencia = models.BooleanField("¿Tiene licencia?", default=False)
    grado_licencia = models.CharField(
        "Grado de licencia", max_length=2, choices=GradoLicencia.choices, blank=True
    )
    activo = models.BooleanField("Activo", default=True)
    notas = models.TextField("Notas", blank=True)
    creado = models.DateTimeField("Creado", auto_now_add=True)
    actualizado = models.DateTimeField("Actualizado", auto_now=True)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()

    def get_absolute_url(self):
        return reverse("empleado_detalle", args=[self.pk])


class HorasTrabajo(models.Model):
    empleado = models.ForeignKey(
        Empleado,
        to_field="cedula",
        on_delete=models.CASCADE,
        related_name="horas",
        verbose_name="Empleado",
    )
    fecha = models.DateField("Fecha")
    horas = models.DecimalField("Horas trabajadas", max_digits=6, decimal_places=2)
    horas_extra = models.DecimalField(
        "Horas extra", max_digits=6, decimal_places=2, default=0
    )
    descripcion = models.CharField("Descripción", max_length=200, blank=True)
    creado = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        verbose_name = "Registro de horas"
        verbose_name_plural = "Horas de trabajo"
        ordering = ["-fecha", "empleado"]

    def __str__(self):
        return f"{self.empleado.cedula} - {self.fecha} ({self.horas} h)"

    @property
    def total_horas(self):
        return (self.horas or 0) + (self.horas_extra or 0)
