"""
API Views
"""
from django.http import JsonResponse
from .models import Socio


def saldos_api(request):
    """API endpoint para saldos dos sócios"""
    socios = Socio.objects.filter(ativo=True)

    saldos = {}
    for socio in socios:
        saldos[socio.nome] = {
            'nome_completo': socio.nome_completo,
            'saldo': float(socio.calcular_saldo()),
        }

    return JsonResponse(saldos)
