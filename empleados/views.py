from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import (
    EmpleadoForm,
    HorasTrabajoForm,
    UsuarioCrearForm,
    UsuarioEditarForm,
)
from .models import Empleado, HorasTrabajo
from .roles import ADMIN, GERENCIA, rol_de, roles_requeridos


class RolRequeridoMixin:
    """Mixin para vistas basadas en clase: exige login y roles permitidos."""

    roles_permitidos = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if self.roles_permitidos and rol_de(request.user) not in self.roles_permitidos:
            messages.error(request, "No tienes permisos para realizar esta acción.")
            return redirect("empleado_lista")
        return super().dispatch(request, *args, **kwargs)


class IniciarSesionView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


@login_required
def home(request):
    total = Empleado.objects.count()
    activos = Empleado.objects.filter(activo=True).count()
    inactivos = total - activos
    recientes = Empleado.objects.order_by("-creado")[:5]
    context = {
        "total": total,
        "activos": activos,
        "inactivos": inactivos,
        "recientes": recientes,
        "anio": timezone.now().year,
    }
    return render(request, "empleados/home.html", context)


@login_required
def empleado_lista(request):
    q = request.GET.get("q", "").strip()
    orden = request.GET.get("orden", "apellido")
    direccion = request.GET.get("dir", "asc")

    empleados = Empleado.objects.all()

    if q:
        empleados = empleados.filter(
            Q(cedula__icontains=q)
            | Q(nombre__icontains=q)
            | Q(apellido__icontains=q)
            | Q(cargo__icontains=q)
            | Q(departamento__icontains=q)
        )

    campos_validos = {
        "cedula",
        "nombre",
        "apellido",
        "cargo",
        "departamento",
        "salario",
        "fecha_ingreso",
        "activo",
    }
    if orden not in campos_validos:
        orden = "apellido"
    if direccion not in ("asc", "desc"):
        direccion = "asc"

    orden_campo = f"-{orden}" if direccion == "desc" else orden
    empleados = empleados.order_by(orden_campo, "apellido")

    context = {
        "empleados": empleados,
        "q": q,
        "orden": orden,
        "dir": direccion,
    }
    return render(request, "empleados/lista.html", context)


@login_required
def empleado_detalle(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    registros = empleado.horas.order_by("-fecha")
    context = {
        "empleado": empleado,
        "horas_recientes": registros[:5],
        "horas_total": registros.aggregate(t=Sum("horas"))["t"] or 0,
        "horas_extra_total": registros.aggregate(t=Sum("horas_extra"))["t"] or 0,
        "horas_registros": registros.count(),
    }
    return render(request, "empleados/detalle.html", context)


class EmpleadoCrearView(RolRequeridoMixin, CreateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "empleados/form.html"
    roles_permitidos = (ADMIN, GERENCIA)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nuevo empleado"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Empleado creado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los errores del formulario.")
        return super().form_invalid(form)


class EmpleadoEditarView(RolRequeridoMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "empleados/form.html"
    roles_permitidos = (ADMIN, GERENCIA)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar: {self.object.nombre_completo}"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Empleado actualizado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los errores del formulario.")
        return super().form_invalid(form)


class EmpleadoEliminarView(RolRequeridoMixin, DeleteView):
    model = Empleado
    template_name = "empleados/confirmar_eliminar.html"
    success_url = reverse_lazy("empleado_lista")
    roles_permitidos = (ADMIN,)

    def form_valid(self, form):
        messages.success(self.request, "Empleado eliminado.")
        return super().form_valid(form)


@login_required
def horas_lista(request):
    q = request.GET.get("q", "").strip()
    orden = request.GET.get("orden", "fecha")
    direccion = request.GET.get("dir", "desc")

    registros = HorasTrabajo.objects.select_related("empleado")
    if q:
        registros = registros.filter(
            Q(empleado__cedula__icontains=q)
            | Q(empleado__nombre__icontains=q)
            | Q(empleado__apellido__icontains=q)
            | Q(descripcion__icontains=q)
        )

    campos_validos = {"fecha", "horas", "horas_extra", "empleado"}
    if orden not in campos_validos:
        orden = "fecha"
    if direccion not in ("asc", "desc"):
        direccion = "desc"

    orden_campo = f"-{orden}" if direccion == "desc" else orden
    registros = registros.order_by(orden_campo, "empleado")

    total_horas = registros.aggregate(t=Sum("horas"))["t"] or 0
    total_extra = registros.aggregate(t=Sum("horas_extra"))["t"] or 0

    context = {
        "registros": registros,
        "q": q,
        "orden": orden,
        "dir": direccion,
        "total_horas": total_horas,
        "total_extra": total_extra,
        "gran_total": total_horas + total_extra,
    }
    return render(request, "empleados/horas_lista.html", context)


class HorasCrearView(RolRequeridoMixin, CreateView):
    model = HorasTrabajo
    form_class = HorasTrabajoForm
    template_name = "empleados/horas_form.html"
    success_url = reverse_lazy("horas_lista")
    roles_permitidos = (ADMIN, GERENCIA)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Nuevo registro de horas"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Registro de horas creado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los errores del formulario.")
        return super().form_invalid(form)


class HorasEditarView(RolRequeridoMixin, UpdateView):
    model = HorasTrabajo
    form_class = HorasTrabajoForm
    template_name = "empleados/horas_form.html"
    success_url = reverse_lazy("horas_lista")
    roles_permitidos = (ADMIN, GERENCIA)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = f"Editar horas: {self.object.empleado.cedula}"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Registro de horas actualizado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los errores del formulario.")
        return super().form_invalid(form)


class HorasEliminarView(RolRequeridoMixin, DeleteView):
    model = HorasTrabajo
    template_name = "empleados/horas_confirmar_eliminar.html"
    success_url = reverse_lazy("horas_lista")
    roles_permitidos = (ADMIN,)

    def form_valid(self, form):
        messages.success(self.request, "Registro de horas eliminado.")
        return super().form_valid(form)


@roles_requeridos(ADMIN)
def usuario_lista(request):
    usuarios = User.objects.select_related("perfil").order_by("username")
    return render(request, "empleados/usuarios_lista.html", {"usuarios": usuarios})


@roles_requeridos(ADMIN)
def usuario_crear(request):
    if request.method == "POST":
        form = UsuarioCrearForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect("usuario_lista")
        messages.error(request, "Revisa los errores del formulario.")
    else:
        form = UsuarioCrearForm()
    return render(
        request,
        "empleados/usuario_form.html",
        {"form": form, "titulo": "Nuevo usuario"},
    )


@roles_requeridos(ADMIN)
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UsuarioEditarForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect("usuario_lista")
        messages.error(request, "Revisa los errores del formulario.")
    else:
        form = UsuarioEditarForm(instance=usuario)
    return render(
        request,
        "empleados/usuario_form.html",
        {"form": form, "titulo": f"Editar usuario: {usuario.username}"},
    )


@roles_requeridos(ADMIN)
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propio usuario.")
        return redirect("usuario_lista")
    if request.method == "POST":
        nombre = usuario.username
        usuario.delete()
        messages.success(request, f"Usuario '{nombre}' eliminado.")
        return redirect("usuario_lista")
    return render(
        request,
        "empleados/usuario_confirmar_eliminar.html",
        {"usuario": usuario},
    )
