from agentes.agente_identidade import agente_identidade
from agentes.agente_boletim import agente_boletim
from agentes.agente_clima import agente_clima

# 1. Mapeamento central de agentes para facilitar a chamada
AGENTES = {
    "identidade": agente_identidade,
    "boletim": agente_boletim,
    "clima": agente_clima,
}

# 2. Mapeamento de palavras-chave para agentes 
PALAVRAS_CHAVE = {
    "identidade": ["identidade", "rg", "carteira", "documento", "2ª via", "segunda via"],
    "boletim": ["boletim", "b.o", "bo", "ocorrencia", "ocorrência", "policia", "polícia", "crime"],
    "clima": ["clima", "chuva", "tempo", "inundação", "temporal", "alerta", "defesa civil"],
}

def detectar_agente_por_palavra_chave(mensagem: str) -> str:
    """
    Detecta qual agente deve ser acionado baseado nas palavras-chave da mensagem
    """
    msg_lower = mensagem.lower()
    for agente, palavras in PALAVRAS_CHAVE.items():
        if any(palavra in msg_lower for palavra in palavras):
            return agente
    return None

def orquestrador(mensagem: str, contexto=None):
    """
    Orquestrador principal da GurIA
    Gerencia o fluxo entre diferentes agentes especializados
    """
    contexto = contexto or {}
    msg_lower = mensagem.lower().strip()
    agente_ativo = contexto.get("agente_ativo")

    if agente_ativo:
        despedidas = ["tchau", "até logo", "adeus", "cancelar", "sair", "voltar", "menu"]
        if any(desp in msg_lower for desp in despedidas):
            return "Ok, cancelando a operação atual. Se precisar de algo mais, é só chamar! 😊", {}

        agente_funcao = AGENTES.get(agente_ativo)
        if agente_funcao:
            try:
                resposta, novo_contexto = agente_funcao(mensagem, contexto)
                if novo_contexto.get("stage") == "final":
                    novo_contexto.pop("agente_ativo", None)
                    resposta += "\n\n💡 Posso te ajudar com mais alguma coisa?"
                return resposta, novo_contexto
            except Exception as e:
                print(f"Erro no agente {agente_ativo}: {e}")
                return "Ocorreu um erro interno. Vamos recomeçar. O que você precisa?", {}
        else:
            return "Ocorreu um erro, vamos recomeçar. O que você precisa?", {}

    else:
        saudacoes = ["oi", "olá", "hello", "hi", "bom dia", "boa tarde", "boa noite", "eae", "e aí"]
        if any(saud in msg_lower for saud in saudacoes) or msg_lower in ["", "menu", "ajuda", "help"]:
            return (
                "Olá! Eu sou a **GurIA**, a assistente virtual do **RSGOV**. 👋\n\n"
                "Como posso te auxiliar hoje?\n\n"
                "**Identidade** - 2ª via, agendamentos, consultas\n"
                "**Boletim de Ocorrência** - Registros, consultas, orientações\n"
                "**Clima** - Previsão, alertas, Defesa Civil\n\n"
                "*Digite sobre o que você precisa ou mencione uma das opções acima.*"
            ), {}

        despedidas = ["tchau", "até logo", "adeus", "valeu", "obrigado", "obrigada", "bye"]
        if any(desp in msg_lower for desp in despedidas):
            return "Até mais! Se precisar de algo, é só chamar. 😊👋", {}

        agente_detectado = detectar_agente_por_palavra_chave(mensagem)

        if agente_detectado in AGENTES:
            contexto = {"agente_ativo": agente_detectado, "stage": "start"}
            return AGENTES[agente_detectado](mensagem, contexto)
        else:
            return (
                "Hmm, não consegui entender exatamente o que você precisa. 🤔\n\n"
                "Posso te ajudar com:\n\n"
                "**Carteira de Identidade** (2ª via, agendamentos)\n"
                "**Boletim de Ocorrência** (registros, consultas)\n"
                "**Clima** (previsão, alertas)\n\n"
                "Sobre qual desses serviços você gostaria de saber?"
            ), {}

def adicionar_agente(nome: str, funcao_agente, palavras_chave: list):
    """
    Função utilitária para adicionar novos agentes dinamicamente
    """
    AGENTES[nome] = funcao_agente
    PALAVRAS_CHAVE[nome] = palavras_chave

def listar_agentes_disponiveis():
    """
    Retorna lista dos agentes disponíveis
    """
    return list(AGENTES.keys())

def resetar_contexto():
    """
    Utilitário para resetar completamente o contexto
    """
    return {}

# Teste simulando uma conversa REAL com mais cenários
if __name__ == "__main__":
    print("🤖 TESTANDO ORQUESTRADOR GURIA")
    print("=" * 50)
    
    # Cenário 1: Conversa básica sobre identidade
    print("\n📋 CENÁRIO 1: Conversa sobre identidade")
    print("-" * 30)
    
    conversa1 = [
        "Olá",
        "Quero fazer a 2ª via da identidade",
        "1",  # Agendar 2ª via
        "sim", # Aceita LGPD
        "João Silva Santos",
        "sair"  # Cancela no meio
    ]
    
    contexto_sessao = None
    
    for msg in conversa1:
        resposta, contexto_sessao = orquestrador(msg, contexto_sessao)
        print(f"👤 Usuário: {msg}")
        print(f"🤖 GurIA: {resposta}")
        print(f"📊 Contexto: {contexto_sessao}")
        print()
    
    # Cenário 2: Detecção automática por palavra-chave
    print("\n📋 CENÁRIO 2: Detecção automática")
    print("-" * 30)
    
    conversa2 = [
        "Preciso fazer um boletim de ocorrência",
        "menu",  # Volta ao menu
        "tchau"
    ]
    
    contexto_sessao = None
    
    for msg in conversa2:
        resposta, contexto_sessao = orquestrador(msg, contexto_sessao)
        print(f"👤 Usuário: {msg}")
        print(f"🤖 GurIA: {resposta}")
        print(f"📊 Contexto: {contexto_sessao}")
        print()
    
    # Cenário 3: Mensagem não reconhecida
    print("\n📋 CENÁRIO 3: Mensagem não reconhecida")
    print("-" * 30)
    
    conversa3 = [
        "Quero saber sobre aliens"
    ]
    
    contexto_sessao = None
    
    for msg in conversa3:
        resposta, contexto_sessao = orquestrador(msg, contexto_sessao)
        print(f"👤 Usuário: {msg}")
        print(f"🤖 GurIA: {resposta}")
        print(f"📊 Contexto: {contexto_sessao}")
        print()
    
    print("✅ TESTES CONCLUÍDOS!")
    print(f"🔧 Agentes disponíveis: {listar_agentes_disponiveis()}")
