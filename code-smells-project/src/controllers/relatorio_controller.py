from src.models import pedido_model
from src.models.constants import FAIXAS_DESCONTO


def desconto_para(faturamento):
    return next((faturamento * taxa for limite, taxa in FAIXAS_DESCONTO if faturamento > limite), 0)


def vendas():
    resumo = pedido_model.resumo_vendas()
    total_pedidos = resumo["total_pedidos"]
    faturamento = resumo["faturamento"]
    desconto = desconto_para(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": resumo["pendentes"],
        "pedidos_aprovados": resumo["aprovados"],
        "pedidos_cancelados": resumo["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
