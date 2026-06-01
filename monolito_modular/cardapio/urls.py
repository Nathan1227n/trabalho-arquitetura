from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemCardapioViewSet

router = DefaultRouter()
router.register(r'itens', ItemCardapioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]