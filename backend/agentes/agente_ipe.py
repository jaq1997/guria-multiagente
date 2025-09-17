import logging
import re

logger = logging.getLogger(__name__)

def agente_ipe(mensagem, contexto=None):
    try:
        logger.debug(f"Agente IPE chamado - Mensagem: '{mensagem}', Contexto: {contexto}")

        if contexto is None:
            contexto = {}

        etapa = contexto.get("etapa", "inicio")
        logger.debug(f"Etapa atual: {etapa}")

        estabelecimentos = {
            "Porto Alegre": [
                {"nome": "Hospital Moinhos de Vento", "tipo": "Hospital", "servicos": ["ortopedista", "clínico geral", "pediatria"], "endereco": "Rua Ramiro Barcelos, 910", "telefone": "(51) 3314-3000"},
                {"nome": "Clínica Mãe de Deus", "tipo": "Clínica", "servicos": ["dentista", "ortopedia", "fisioterapia"], "endereco": "Rua José de Alencar, 286", "telefone": "(51) 3230-3600"},
                {"nome": "Hospital de Clínicas", "tipo": "Hospital", "servicos": ["cardiologia", "neurologia"], "endereco": "Rua Ramiro Barcelos, 2350", "telefone": "(51) 3359-8000"}
            ],
            "Canoas": [
                {"nome": "Hospital Universitário", "tipo": "Hospital", "servicos": ["cardiologia", "fisioterapia"], "endereco": "Av. Farroupilha, 8001", "telefone": "(51) 3612-1200"},
                {"nome": "Clínica São Vicente", "tipo": "Clínica", "servicos": ["dentista", "ortopedia"], "endereco": "Rua Tiradentes, 235", "telefone": "(51) 3472-3456"}
            ]
        }

        # Lista de palavras para ignorar na mensagem do usuário
        stopwords = ["em", "de", "para", "o", "a", "as", "os", "no", "na"]

        if etapa == "inicio":
            resposta = (
                "🏥 Certo, sobre IPE Saúde posso te mostrar os hospitais e clínicas credenciadas.\n\n"
                "Me conta de que cidade tu fala e qual atendimento procuras (ou se procura por algum específico)."
            )
            contexto.update({
                "etapa": "aguarde_cidade_e_filtro",
                "agente_ativo": "ipe"
            })
            logger.debug("Etapa definida como 'aguarde_cidade_e_filtro'")
            return resposta, contexto

        elif etapa == "aguarde_cidade_e_filtro":
            texto = mensagem.strip().lower()

            cidades_disponiveis = [c.lower() for c in estabelecimentos.keys()]
            cidade_encontrada = None
            filtro = ""

            # Tentar extrair cidade e atendimento mais robustamente
            for cidade in cidades_disponiveis:
                if cidade in texto:
                    cidade_encontrada = cidade.title()
                    # remover cidade da mensagem
                    texto_sem_cidade = texto.replace(cidade, "")
                    # separar palavras e remover stopwords para obter filtro
                    palavras = [p for p in re.split(r"\s+", texto_sem_cidade.strip()) if p and p not in stopwords]
                    filtro = " ".join(palavras)
                    break

            if not cidade_encontrada:
                resposta = (
                    "❌ Não consegui identificar a cidade. As cidades disponíveis são:\n"
                    "• Porto Alegre\n• Canoas\n\n"
                    "Por favor, informe a cidade e, se quiser, o atendimento."
                )
                return resposta, contexto

            contexto.update({
                "cidade": cidade_encontrada,
                "agente_ativo": "ipe"
            })

            lista_estabelecimentos = estabelecimentos.get(cidade_encontrada, [])

            if filtro:
                filtro = filtro.lower()
                lista_filtrada = []
                for est in lista_estabelecimentos:
                    servicos = [s.lower() for s in est.get("servicos", [])]
                    # verificar se filtro está exatamente nos serviços ou está substring de algum serviço
                    if filtro in servicos or any(filtro in s for s in servicos):
                        lista_filtrada.append(est)
                if not lista_filtrada:
                    resposta = (
                        f"❌ Não encontrei estabelecimentos com atendimento de '{filtro}' em {cidade_encontrada}.\n"
                        "Tente outro atendimento ou digite 'menu' para voltar."
                    )
                    contexto["etapa"] = "aguarde_cidade_e_filtro"
                    return resposta, contexto
            else:
                lista_filtrada = lista_estabelecimentos

            resposta = f"🏥 Estabelecimentos IPE Saúde em {cidade_encontrada}"
            if filtro:
                resposta += f" com atendimento de '{filtro}'"
            resposta += ":\n\n"

            for est in lista_filtrada:
                resposta += f"• {est['nome']} ({est['tipo']})\n"
                resposta += f"  📍 {est['endereco']}\n"
                resposta += f"  📞 {est['telefone']}\n\n"

            resposta += (
                "ℹ️ Se quiser consultar outro atendimento ou cidade, digite a nova consulta.\n"
                "Para sair, digite 'menu'."
            )

            contexto["etapa"] = "pos_consulta"
            return resposta, contexto

        elif etapa == "pos_consulta":
            msg_lower = mensagem.lower().strip()

            if msg_lower in ["menu", "voltar", "sair", "cancelar"]:
                resposta = (
                    "✅ Consulta encerrada. Se precisar de algo mais, estou aqui para ajudar! 😊"
                )
                contexto = {"stage": "final"}
                logger.debug("Finalizando agente IPE")
                return resposta, contexto

            contexto["etapa"] = "aguarde_cidade_e_filtro"
            return agente_ipe(mensagem, contexto)

        else:
            logger.warning(f"Etapa desconhecida: {etapa}")
            resposta = (
                "❓ Houve um problema na conversa.\n"
                "Por favor, informe sua cidade e atendimento (se quiser) para consultar estabelecimentos credenciados."
            )
            contexto.update({
                "etapa": "aguarde_cidade_e_filtro",
                "agente_ativo": "ipe"
            })
            return resposta, contexto

    except Exception as e:
        logger.error(f"Erro no agente IPE: {str(e)}")
        return (
            "❌ Ocorreu um erro na consulta IPE Saúde.\n"
            "Por favor, tente novamente ou digite 'menu' para voltar ao início."
        ), {"stage": "final"}
