from pathlib import Path
import shutil
import uuid

from auth import verificar_login, criar_token, verificar_token

from fastapi import (
    FastAPI,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    Header
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Obra, Admin


# =========================================================
# BANCO DE DADOS
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# APLICAÇÃO
# =========================================================

app = FastAPI(
    title="Museu das Coisas Bonitas API",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# UPLOADS
# =========================================================

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.get("/")
def inicio():
    return FileResponse("index.html")


# =========================================================
# PAINEL ADMINISTRATIVO
# =========================================================

@app.get("/admin")
def pagina_admin():
    return FileResponse("admin.html")


# =========================================================
# VERIFICAR ADMINISTRADOR
# =========================================================

def verificar_admin(
    authorization: str = Header(None)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Autenticação necessária"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    token = authorization.split(" ", 1)[1]

    if not verificar_token(token):
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    return 1


# =========================================================
# LOGIN
# =========================================================

@app.post("/api/login")
def login(
    username: str = Form(...),
    senha: str = Form(...)
):

    if not verificar_login(username, senha):

        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas"
        )

    return {
        "mensagem": "Login realizado com sucesso",
        "access_token": criar_token(1),
        "token_type": "bearer"
    }


# =========================================================
# LISTAR OBRAS
# =========================================================

@app.get("/api/obras")
def listar_obras(
    db: Session = Depends(get_db)
):

    obras = db.query(Obra).all()

    return {
        "obras": [
            {
                "id": obra.id,
                "titulo": obra.titulo,
                "categoria": obra.categoria,
                "descricao": obra.descricao,
                "imagem": obra.imagem
            }
            for obra in obras
        ]
    }


# =========================================================
# ADICIONAR OBRA
# =========================================================

@app.post("/api/obras")
def adicionar_obra(
    titulo: str = Form(...),
    categoria: str = Form(...),
    descricao: str = Form(""),
    imagem: UploadFile = File(...),
    admin_id: int = Depends(verificar_admin),
    db: Session = Depends(get_db)
):

    extensao = Path(
        imagem.filename
    ).suffix.lower()

    nome_arquivo = f"{uuid.uuid4()}{extensao}"

    caminho = UPLOAD_DIR / nome_arquivo

    with caminho.open("wb") as arquivo:

        shutil.copyfileobj(
            imagem.file,
            arquivo
        )

    nova_obra = Obra(
        titulo=titulo,
        categoria=categoria,
        descricao=descricao,
        imagem=f"/uploads/{nome_arquivo}"
    )

    db.add(nova_obra)

    db.commit()

    db.refresh(nova_obra)

    return {
        "mensagem": "Obra adicionada com sucesso!",
        "obra": {
            "id": nova_obra.id,
            "titulo": nova_obra.titulo,
            "categoria": nova_obra.categoria,
            "descricao": nova_obra.descricao,
            "imagem": nova_obra.imagem
        }
    }


# =========================================================
# EDITAR OBRA
# =========================================================

@app.put("/api/obras/{obra_id}")
def editar_obra(
    obra_id: int,
    titulo: str = Form(...),
    categoria: str = Form(...),
    descricao: str = Form(""),
    imagem: UploadFile | None = File(None),
    admin_id: int = Depends(verificar_admin),
    db: Session = Depends(get_db)
):

    obra = db.query(Obra).filter(
        Obra.id == obra_id
    ).first()

    if not obra:

        raise HTTPException(
            status_code=404,
            detail="Obra não encontrada"
        )

    obra.titulo = titulo
    obra.categoria = categoria
    obra.descricao = descricao

    if imagem and imagem.filename:

        extensao = Path(
            imagem.filename
        ).suffix.lower()

        nome_arquivo = f"{uuid.uuid4()}{extensao}"

        caminho = UPLOAD_DIR / nome_arquivo

        with caminho.open("wb") as arquivo:

            shutil.copyfileobj(
                imagem.file,
                arquivo
            )

        obra.imagem = f"/uploads/{nome_arquivo}"

    db.commit()

    db.refresh(obra)

    return {
        "mensagem": "Obra atualizada com sucesso!",
        "obra": {
            "id": obra.id,
            "titulo": obra.titulo,
            "categoria": obra.categoria,
            "descricao": obra.descricao,
            "imagem": obra.imagem
        }
    }


# =========================================================
# APAGAR OBRA
# =========================================================

@app.delete("/api/obras/{obra_id}")
def apagar_obra(
    obra_id: int,
    admin_id: int = Depends(verificar_admin),
    db: Session = Depends(get_db)
):

    obra = db.query(Obra).filter(
        Obra.id == obra_id
    ).first()

    if not obra:

        raise HTTPException(
            status_code=404,
            detail="Obra não encontrada"
        )

    if obra.imagem:

        caminho_imagem = Path(
            obra.imagem.lstrip("/")
        )

        if caminho_imagem.exists():

            caminho_imagem.unlink()

    db.delete(obra)

    db.commit()

    return {
        "mensagem": "Obra apagada com sucesso!"
    }