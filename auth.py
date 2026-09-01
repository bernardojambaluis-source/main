ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123456"


def verificar_login(username, senha):
    return (
        username == ADMIN_USERNAME
        and senha == ADMIN_PASSWORD
    )


def criar_token(admin_id):
    return "museu-admin"


def verificar_token(token):
    return token == "museu-admin"