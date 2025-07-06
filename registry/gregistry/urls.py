from django.urls import include, path
from rest_framework import routers

from gregistry.apis.usuario_viewset import AuthViewSet, UserViewSet
from gregistry.apis.evento_viewset import EventoViewSet
from gregistry.apis.regalo_viewset import RegaloViewSet
router = routers.DefaultRouter()
router.register("regalos", RegaloViewSet, basename="regalo")
router.register("usuarios", UserViewSet, basename='usuarios')
router.register('eventos', EventoViewSet, basename='evento')
router.register("auth", AuthViewSet,basename="auth")
urlpatterns = [
    path('',include(router.urls)),

]
