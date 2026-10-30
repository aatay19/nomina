from django.urls import path

from . import views

urlpatterns = [
    path("", views.horas_lista, name="horas_lista"),
    path("nuevo/", views.HorasCrearView.as_view(), name="horas_crear"),
    path("<int:pk>/editar/", views.HorasEditarView.as_view(), name="horas_editar"),
    path(
        "<int:pk>/eliminar/",
        views.HorasEliminarView.as_view(),
        name="horas_eliminar",
    ),
]
