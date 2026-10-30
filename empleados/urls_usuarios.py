from django.urls import path

from . import views

urlpatterns = [
    path("", views.usuario_lista, name="usuario_lista"),
    path("nuevo/", views.usuario_crear, name="usuario_crear"),
    path("<int:pk>/editar/", views.usuario_editar, name="usuario_editar"),
    path("<int:pk>/eliminar/", views.usuario_eliminar, name="usuario_eliminar"),
]
