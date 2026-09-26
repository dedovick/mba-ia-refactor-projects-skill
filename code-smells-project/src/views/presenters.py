PRODUTO_FIELDS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")
USUARIO_FIELDS = ("id", "nome", "email", "tipo", "criado_em")
USUARIO_LOGIN_FIELDS = ("id", "nome", "email", "tipo")


def _pick(entity, fields):
    return {field: entity[field] for field in fields if field in entity}


def present_produto(produto):
    return _pick(produto, PRODUTO_FIELDS)


def present_usuario(usuario):
    return _pick(usuario, USUARIO_FIELDS)


def present_usuario_login(usuario):
    return _pick(usuario, USUARIO_LOGIN_FIELDS)


def sucesso(dados=None, status=200, **extra):
    corpo = {}
    if dados is not None:
        corpo["dados"] = dados
    corpo["sucesso"] = True
    corpo.update(extra)
    return corpo, status
