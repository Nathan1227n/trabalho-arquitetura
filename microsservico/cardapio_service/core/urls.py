from django.contrib import admin
from django.urls import path, include
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class HealthCheckView(APIView):
    def get(self, request):
        return Response(
            {"status": "ok", "service": "cardapio"},
            status=status.HTTP_200_OK,
        )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('cardapio/', include('cardapio.urls')),
    path('health/', HealthCheckView.as_view(), name='health'),
]
