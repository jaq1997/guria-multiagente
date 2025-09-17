from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from conexao.orquestrador import orquestrador
import uuid
import shutil
from pathlib import Path
import traceback
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mudei para aceitar qualquer origem durante desenvolvimento
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
        
        # Se não há session_id ou sessão não existe, criar nova
        if not session_id or session_id not in sessoes_ativas:
            session_id = str(uuid.uuid4())
            contexto = {}
        else:
            # Usar o contexto completo da sessão existente
            contexto = sessoes_ativas[session_id].copy()

        # Sincronizar documentos enviados com documentos recebidos
        documentos_anexados = contexto.get("documentos_enviados", [])
        contexto["documentos_recebidos"] = documentos_anexados.copy()

        logger.debug(f"Chat - Session ID: {session_id}")
        logger.debug(f"Chat - Contexto antes do orquestrador: {contexto}")

        resposta, novo_contexto = orquestrador(mensagem, contexto)

        # Preservar session_id no novo contexto
        novo_contexto["session_id"] = session_id
        
        # Atualizar a sessão ativa com o novo contexto completo
        sessoes_ativas[session_id] = novo_contexto

        logger.debug(f"Chat - Novo contexto salvo: {novo_contexto}")

        return {
            "reply": resposta,
            "contexto": novo_contexto,
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Erro no chat: {str(e)}")
        traceback.print_exc()
        error_session_id = data.session_id or str(uuid.uuid4())
        return {
            "reply": f"Desculpe, ocorreu um erro interno: {str(e)}. Tente novamente.",
            "contexto": {},
            "session_id": error_session_id
        }

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    tipo_documento: Optional[str] = Form(None)  # Tornar opcional
):
    try:
        logger.debug(f"Recebendo upload - Session ID: {session_id}, Tipo: {tipo_documento}, Arquivo: {file.filename}")
        
        # Validar se o arquivo foi enviado
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="Nenhum arquivo foi enviado")
        
        # Criar diretório da sessão
        session_dir = UPLOAD_DIRECTORY / session_id
        session_dir.mkdir(exist_ok=True)

        # Salvar arquivo
        file_path = session_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Determinar tipo do documento baseado no nome do arquivo se não foi fornecido
        if not tipo_documento:
            filename_lower = file.filename.lower()
            if any(word in filename_lower for word in ['rg', 'identidade', 'carteira']):
                tipo_documento = 'rg'
            elif any(word in filename_lower for word in ['certidao', 'certidão', 'nascimento', 'casamento']):
                tipo_documento = 'certidao'
            elif any(word in filename_lower for word in ['comprovante', 'residencia', 'residência', 'endereco']):
                tipo_documento = 'comprovante'
            elif any(word in filename_lower for word in ['cpf']):
                tipo_documento = 'cpf'
            else:
                tipo_documento = 'documento'

        # Atualizar contexto da sessão
        if session_id not in sessoes_ativas:
            sessoes_ativas[session_id] = {
                "documentos_enviados": [],
                "session_id": session_id
            }
        
        # Garantir que a lista de documentos existe
        if "documentos_enviados" not in sessoes_ativas[session_id]:
            sessoes_ativas[session_id]["documentos_enviados"] = []
        
        # Adicionar apenas se não existe
        if tipo_documento not in sessoes_ativas[session_id]["documentos_enviados"]:
            sessoes_ativas[session_id]["documentos_enviados"].append(tipo_documento)

        logger.debug(f"Arquivo salvo com sucesso: {file_path}")
        logger.debug(f"Contexto completo da sessão após upload: {sessoes_ativas[session_id]}")

        return {
            "message": f"Arquivo '{file.filename}' do tipo '{tipo_documento}' enviado com sucesso!",
            "status": "sucesso",
            "filename": file.filename,
            "tipo_documento": tipo_documento
        }
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Não foi possível salvar o arquivo: {str(e)}"
        )