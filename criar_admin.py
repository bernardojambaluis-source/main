from database import Base, engine, SessionLocal
from models import Admin
from auth import criar_hash_senha

Base.metadata.create_all(bind=engine)

db = SessionLocal()

username = input("Nome do administrador: ")
senha = input("Senha do administrador: ")

admin_existente = db.query(Admin).filter(
    Admin.username == username
).first()

if admin_existente:
    print("Esse administrador já existe.")
else:
    admin = Admin(
        username=username,
        senha_hash=criar_hash_senha(senha)
    )

    db.add(admin)
    db.commit()

    print("Administrador criado com sucesso!")

db.close()