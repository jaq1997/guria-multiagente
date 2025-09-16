from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from conexao.orquestrador import orquestrador
import uuid
import shutil
from pathlib import Path
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)

sessoes_ativas: Dict[str, Dict[str, Any]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.get("/")
async def health_check():
    return {
        "status": "ok", 
        "message": "GurIA API está funcionando!",
        "sessoes_ativas": len(sessoes_ativas)
    }

@app.post("/chat")
async def chat(data: ChatRequest):
    try:
        mensagem = data.message
        session_id = data.session_id

        if not session_id or session_id not in sessoes_ativas:
            session_id = str(uuid.uuid4())
            contexto = {}
        else:
            contexto = sessoes_ativas[session_id]

        # Sincroniza arquivos anexados para o contexto do agente
        documentos_anexados = contexto.get("documentos_enviados", [])
        contexto["documentos_recebidos"] = documentos_anexados.copy()

        resposta, novo_contexto = orquestrador(mensagem, contexto)

        sessoes_ativas[session_id] = novo_contexto

        response_data = {
            "reply": resposta, 
            "contexto": novo_contexto, 
            "session_id": session_id
        }

        return response_data

    except Exception as e:
        error_session_id = data.session_id or str(uuid.uuid4())
        return {
            "reply": f"Desculpe, ocorreu um erro interno: {str(e)}. Tente novamente.",
            "contexto": {},
            "session_id": error_session_id
        }

@app.post("/upload-document")
async def upload_document(session_id: str = Form(...), file: UploadFile = File(...)):
    try:
        session_dir = UPLOAD_DIRECTORY / session_id
        session_dir.mkdir(exist_ok=True)

        file_path = session_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if session_id in sessoes_ativas:
            if "documentos_enviados" not in sessoes_ativas[session_id]:
                sessoes_ativas[session_id]["documentos_enviados"] = []
            sessoes_ativas[session_id]["documentos_enviados"].append(file.filename)

        return {"status": "sucesso", "filename": file.filename}

    except Exception as e:
        traceback.print_exc()
        return {"status": "erro", "message": f"Não foi possível salvar o arquivo: {str(e)}"}
