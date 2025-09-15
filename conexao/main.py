from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from conexao.orquestrador import orquestrador
import uuid
import shutil
from pathlib import Path
import traceback
import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  # Adicionado
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NOVO: Bloco para gerenciamento de uploads ---
UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)

# Dicionário para guardar a "memória" (contexto) de cada conversa no servidor.
sessoes_ativas: Dict[str, Dict[str, Any]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.get("/")
async def health_check():
    """Endpoint para testar se o servidor está funcionando"""
    return {
        "status": "ok", 
        "message": "GurIA API está funcionando!",
        "sessoes_ativas": len(sessoes_ativas)
    }

@app.get("/test-orquestrador")
async def test_orquestrador():
    """Testa o orquestrador diretamente"""
    try:
        print("🧪 Testando orquestrador...")
        resposta, contexto = orquestrador("Olá", {})
        print(f"✅ Teste OK: {resposta}")
        return {
            "status": "success",
            "resposta": resposta,
            "contexto": contexto
        }
    except Exception as e:
        print(f"❌ Erro no teste do orquestrador: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/chat")
async def chat(data: ChatRequest):
    try:
        print(f"\n🔵 === NOVA REQUISIÇÃO ===")
        print(f"🔵 Mensagem recebida: '{data.message}'")
        print(f"🔵 Session ID recebido: {data.session_id}")
        print(f"🔵 Sessões ativas atualmente: {len(sessoes_ativas)}")
        
        mensagem = data.message
        session_id = data.session_id

        # Se não veio um ID de sessão, é uma nova conversa. Criamos um ID novo.
        if not session_id or session_id not in sessoes_ativas:
            session_id = str(uuid.uuid4())
            contexto = {}
            print(f"🟡 Nova sessão criada: {session_id}")
            print(f"🟡 Contexto inicial: {contexto}")
        else:
            # Se o ID já existe, carregamos o contexto salvo da memória do servidor.
            contexto = sessoes_ativas[session_id]
            print(f"🟡 Sessão existente: {session_id}")
            print(f"🟡 Contexto carregado: {contexto}")

        # TESTE: Vamos testar o orquestrador antes de chamar
        print(f"🔄 Chamando orquestrador com:")
        print(f"   - Mensagem: '{mensagem}'")
        print(f"   - Contexto: {contexto}")
        
        # Chamamos o orquestrador com o contexto que o SERVIDOR guardou.
        resposta, novo_contexto = orquestrador(mensagem, contexto)
        
        print(f"✅ Orquestrador retornou:")
        print(f"   - Resposta: '{resposta}'")
        print(f"   - Novo contexto: {novo_contexto}")

        # ATUALIZAMOS a memória do servidor com o novo contexto da conversa.
        sessoes_ativas[session_id] = novo_contexto
        print(f"💾 Contexto salvo na sessão {session_id}")

        # Monta a resposta
        response_data = {
            "reply": resposta, 
            "contexto": novo_contexto, 
            "session_id": session_id
        }
        
        print(f"📤 Enviando resposta: {response_data}")
        print(f"🔵 === FIM DA REQUISIÇÃO ===\n")
        
        return response_data

    except Exception as e:
        print(f"\n❌ === ERRO NA REQUISIÇÃO ===")
        print(f"❌ Erro: {e}")
        print(f"❌ Tipo do erro: {type(e)}")
        print(f"❌ Traceback completo:")
        traceback.print_exc()
        
        # Cria um session_id se não existir para evitar erro no frontend
        error_session_id = data.session_id or str(uuid.uuid4())
        
        error_response = {
            "reply": f"Desculpe, ocorreu um erro interno: {str(e)}. Tente novamente.",
            "contexto": {},
            "session_id": error_session_id
        }
        
        print(f"📤 Enviando resposta de erro: {error_response}")
        print(f"❌ === FIM DO ERRO ===\n")
        
        return error_response

@app.get("/debug-sessions")
async def debug_sessions():
    """Endpoint para debug das sessões"""
    return {
        "total_sessoes": len(sessoes_ativas),
        "sessoes": {
            session_id: {
                "contexto": str(contexto)[:200] + "..." if len(str(contexto)) > 200 else contexto,
                "keys": list(contexto.keys()) if isinstance(contexto, dict) else "não é dict"
            }
            for session_id, contexto in sessoes_ativas.items()
        }
    }

@app.delete("/clear-sessions")
async def clear_all_sessions():
    """Limpa todas as sessões (útil para testes)"""
    global sessoes_ativas
    total = len(sessoes_ativas)
    sessoes_ativas.clear()
    return {"message": f"{total} sessões foram limpas"}

# --- Endpoint para Upload de Documentos ---
@app.post("/upload-document")
async def upload_document(session_id: str = Form(...), file: UploadFile = File(...)):
    """
    Este endpoint recebe um arquivo e um session_id,
    e salva o arquivo no servidor dentro de uma pasta com o nome do ID da sessão.
    """
    try:
        print(f"📎 Upload recebido - Session: {session_id}, Arquivo: {file.filename}")
        
        # Garante que o diretório para a sessão específica exista
        session_dir = UPLOAD_DIRECTORY / session_id
        session_dir.mkdir(exist_ok=True)

        # Define o caminho completo do arquivo e salva
        file_path = session_dir / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"✅ Arquivo '{file.filename}' salvo para a sessão '{session_id}' em '{file_path}'")
        
        # Opcional: Atualiza o contexto para indicar que o upload foi feito
        if session_id in sessoes_ativas:
            if "documentos_enviados" not in sessoes_ativas[session_id]:
                sessoes_ativas[session_id]["documentos_enviados"] = []
            sessoes_ativas[session_id]["documentos_enviados"].append(file.filename)
            print(f"📋 Contexto atualizado para {session_id}: {sessoes_ativas[session_id]}")

        return {"status": "sucesso", "filename": file.filename}
        
    except Exception as e:
        print(f"❌ Erro no upload: {e}")
        traceback.print_exc()
        return {"status": "erro", "message": f"Não foi possível salvar o arquivo: {str(e)}"}

# Função para testar na inicialização
def test_orquestrador_on_startup():
    """Testa o orquestrador quando o servidor inicia"""
    try:
        print("🚀 Testando orquestrador na inicialização...")
        resposta, contexto = orquestrador("Teste de inicialização", {})
        print(f"✅ Orquestrador funcionando: {resposta[:50]}...")
        return True
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: Orquestrador não está funcionando!")
        print(f"❌ Erro: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 INICIANDO GURIA API")
    print("=" * 60)
    
    # Testa o orquestrador antes de iniciar
    if test_orquestrador_on_startup():
        print("✅ Pré-teste passou, iniciando servidor...")
    else:
        print("❌ Pré-teste falhou, mas iniciando mesmo assim...")
    
    import uvicorn
    print(f"🔗 Health Check: http://localhost:8000/")
    print(f"🧪 Test Orquestrador: http://localhost:8000/test-orquestrador")
    print(f"💬 Chat: http://localhost:8000/chat")
    print(f"🐛 Debug Sessions: http://localhost:8000/debug-sessions")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)