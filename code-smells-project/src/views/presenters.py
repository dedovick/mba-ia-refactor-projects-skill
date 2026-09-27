CAMPOS_PRODUTO = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")
CAMPOS_USUARIO = ("id", "nome", "email", "tipo", "criado_em")
CAMPOS_LOGIN = ("id", "nome", "email", "tipo")


def _pick(origem, campos):
    return {campo: origem[campo] for campo in campos if campo in origem}


def present_produto(produto):
    return _pick(produto, CAMPOS_PRODUTO)


def present_usuario(usuario):
    return _pick(usuario, CAMPOS_USUARIO)


def present_login(usuario):
    return _pick(usuario, CAMPOS_LOGIN)


def present_pedido(pedido):
    return {
        "id": pedido["id"],
        "usuario_id": pedido["usuario_id"],
        "status": pedido["status"],
        "total": pedido["total"],
        "criado_em": pedido["criado_em"],
        "itens": [
            {
                "produto_id": item["produto_id"],
                "produto_nome": item["produto_nome"],
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"],
            }
            for item in pedido["itens"]
        ],
    }
