from django.urls import path

from . import views

urlpatterns = [
    path("", views.empleado_lista, name="empleado_lista"),
    path("nuevo/", views.EmpleadoCrearView.as_view(), name="empleado_crear"),
    path("<int:pk>/", views.empleado_detalle, name="empleado_detalle"),
    path("<int:pk>/editar/", views.EmpleadoEditarView.as_view(), name="empleado_editar"),
    path(
        "<int:pk>/eliminar/",
        views.EmpleadoEliminarView.as_view(),
        name="empleado_eliminar",
    ),
]
