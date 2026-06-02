from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class NotificacaoHealthView(APIView):
    def get(self, request):
        return Response(
            {"status": "ok", "service": "notificacao"},
            status=status.HTTP_200_OK,
        )
