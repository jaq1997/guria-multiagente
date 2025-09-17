from agentes.agente_identidade import agente_identidade
from agentes.agente_boletim import agente_boletim
from agentes.agente_clima import agente_clima
from agentes.agente_ipe import agente_ipe
from agentes.agente_seduc import agente_seduc
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

AGENTES = {
    "identidade": agente_identidade,
    "boletim": agente_boletim,
    "clima": agente_clima,
    "ipe": agente_ipe,
    "seduc": agente_seduc,
}

PALAVRAS_CHAVE = {
    "identidade": ["identidade", "rg", "carteira", "documento", "2ª via", "segunda via"],
    "boletim": ["boletim", "b.o", "bo", "ocorrencia", "ocorrência", "policia", "polícia", "crime", "assalto"],
    "clima": ["clima", "chuva", "tempo", "inundação", "temporal", "alerta", "defesa civil", "previsão", "enchente"],
    "ipe": ["ipe", "clinica", "hospital", "saúde", "ipe saúde"],
    "seduc": ["seduc", "matricula", "histórico", "vagas", "rematricula", "rematrícula", "escolas", "escola"],
}

def detectar_agente_por_palavra_chave(mensagem: str) -> str:
    msg_lower = mensagem.lower()
    logger.debug(f"Detectando agente para mensagem: '{msg_lower}'")
    for agente, palavras in PALAVRAS_CHAVE.items():
        if any(palavra in msg_lower for palavra in palavras):
            logger.debug(f"Agente '{agente}' detectado pela palavra-chave")
            return agente
    logger.debug("Nenhum agente detectado por palavra-chave")
    return None

def orquestrador(mensagem: str, contexto=None):
    try:
        logger.debug(f"Orquestrador iniciado - Mensagem: '{mensagem}', Contexto: {contexto}")
        contexto = contexto or {}
        msg_lower = mensagem.lower().strip()
        agente_ativo = contexto.get("agente_ativo")
        logger.debug(f"Agente ativo atual: {agente_ativo}")

        despedidas = ["tchau", "até logo", "adeus", "cancelar", "sair", "voltar", "menu"]
        confirma_aceita = ["pronto", "ok", "enviado", "enviei", "confirmo"]

        if any(desp in msg_lower for desp in despedidas):
            logger.debug("Despedida detectada")
            return "Ok, cancelando a operação atual. Se precisar de algo mais, é só chamar! 😊", {}

        if agente_ativo:
            if msg_lower in confirma_aceita:
                documentos_recebidos = contexto.get("documentos_recebidos", [])
                if "rg" in documentos_recebidos and "comprovante" in documentos_recebidos:
                    novo_contexto = contexto.copy()
                    novo_contexto.pop("agente_ativo", None)
                    novo_contexto.pop("stage", None)
                    logger.debug("Documentos confirmados recebidos")
                    return "Documentos recebidos. Vamos continuar o atendimento.", novo_contexto
                else:
                    logger.debug("Ainda faltam documentos")
                    return "Ainda não recebi ambos os documentos (RG/Identidade e Comprovante/Residência). Por favor, envie ambos e digite 'pronto'.", contexto
            agente_funcao = AGENTES.get(agente_ativo)
            if agente_funcao:
                try:
                    resposta, novo_contexto = agente_funcao(mensagem, contexto)
                    logger.debug(f"Resposta do agente: '{resposta}', Novo contexto: {novo_contexto}")
                    if novo_contexto.get("stage") == "final" or novo_contexto.get("etapa") == "final":
                        novo_contexto.pop("agente_ativo", None)
                        resposta += "\n\n💡 Posso ajudar com mais alguma coisa?"
                        logger.debug("Agente finalizado")
                    return resposta, novo_contexto
                except Exception as e:
                    logger.error(f"Erro ao chamar agente {agente_ativo}: {str(e)}")
                    return f"Ocorreu um erro interno ({str(e)}). Vamos recomeçar. O que você precisa?", {}
            else:
                logger.error(f"Agente {agente_ativo} não encontrado em AGENTES")
                return "Erro no agente ativo. Vamos recomeçar.", {}

        agente_detectado = detectar_agente_por_palavra_chave(mensagem)
        logger.debug(f"Agente detectado: {agente_detectado}")

        if agente_detectado and agente_detectado in AGENTES:
            contexto = {"agente_ativo": agente_detectado, "stage": "start", "etapa": "inicio"}
            try:
                logger.debug(f"Iniciando agente: {agente_detectado}")
                resposta, novo_contexto = AGENTES[agente_detectado](mensagem, contexto)
                logger.debug(f"Agente {agente_detectado} iniciado com sucesso")
                return resposta, novo_contexto
            except Exception as e:
                logger.error(f"Erro ao iniciar agente {agente_detectado}: {str(e)}")
                return f"Erro ao iniciar serviço. Tente novamente.", {}

        saudacoes = ["oi", "olá", "hello", "hi", "bom dia", "boa tarde", "boa noite", "eae", "e aí"]
        if any(saud in msg_lower for saud in saudacoes) or msg_lower in ["", "menu", "ajuda", "help"]:
            logger.debug("Saudação detectada")
            return (
                "Olá! Eu sou a **GurIA**, a assistente virtual do **RSGOV**. 👋\n\n"
                "Como posso te ajudar hoje?\n\n"
                "**Identidade** - 2ª via, agendamentos, consultas\n"
                "**Boletim de Ocorrência** - registros e consultas\n"
                "**Clima** - alertas, previsão, defesa civil\n"
                "**IPE Saúde** - hospitais e clínicas credenciados\n"
                "**SEDUC** - matrícula, histórico, vagas\n\n"
                "*Digite sobre o que você precisa ou escolha uma das opções acima.*"
            ), {}

        logger.debug("Nenhuma condição atendida - retornando mensagem padrão")
        return (
            "Não consegui entender exatamente o que você precisa. Posso ajudar com:\n"
            "- Carteira de Identidade\n"
            "- Boletim de Ocorrência\n"
            "- Clima e Defesa Civil\n"
            "- IPE Saúde\n"
            "- SEDUC\n"
            "Sobre qual desses serviços gostaria de saber?"
        ), {}

    except Exception as e:
        logger.error(f"Erro geral no orquestrador: {str(e)}")
        return f"Erro interno no sistema: {str(e)}", {}
