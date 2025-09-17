import logging

logger = logging.getLogger(__name__)

def mensagem_lgpd():
    return (
        "⚠️ Aviso de Privacidade (LGPD): Para continuar, precisamos coletar e tratar alguns dados pessoais "
        "como nome completo, CPF e documentos. Estes dados serão utilizados exclusivamente para realizar o serviço solicitado. "
        "As informações serão tratadas conforme a Lei Geral de Proteção de Dados (Lei nº 13.709/2018), com segurança e confidencialidade. "
        "Você concorda com o uso dos seus dados para essa finalidade? (sim/não)"
    )

def agente_seduc(mensagem, contexto=None):
    try:
        logger.debug(f"Agente SEDUC chamado - Mensagem: '{mensagem}', Contexto: {contexto}")

        if contexto is None:
            contexto = {}

        etapa = contexto.get("etapa", "inicio")
        logger.debug(f"Etapa atual: {etapa}")

        vagas_cidades = {
            "Porto Alegre": {
                "infantil": ["CENTRO ADM FERNANDO FERRARI", "ARQUITETO BATISTTINO ANELE-DAER"],
                "fundamental": ["ESCOLA ESTADUAL DE ENSINO FUNDAMENTAL COELHO NETO", "INSTITUTO ESTADUAL DOM DIOGO DE SOUZA"],
                "medio": ["COLÉGIO ESTADUAL PROTASIO ALVES", "COLÉGIO ESTADUAL JÚLIO DE CASTILHOS"]
            },
            "Canoas": {
                "infantil": ["CENTRO ADM FERNANDO FERRARI", "ARQUITETO BATISTTINO ANELE-DAER"],
                "fundamental": ["ESCOLA ESTADUAL DE ENSINO FUNDAMENTAL COELHO NETO", "INSTITUTO ESTADUAL DOM DIOGO DE SOUZA"],
                "medio": ["COLÉGIO ESTADUAL PROTASIO ALVES", "COLÉGIO ESTADUAL JÚLIO DE CASTILHOS"]
            }
        }

        if etapa == "inicio":
            resposta = (
                "Certo, sobre SEDUC posso te ajudar com os seguintes serviços:\n"
                "1 - Comprovante de matrícula\n"
                "2 - Histórico escolar\n"
                "3 - Vagas escolares disponíveis\n"
                "4 - Rematrícula\n"
                "Selecione a opção (digite o número correspondente)."
            )
            contexto.update({
                "etapa": "aguarda_servico",
                "agente_ativo": "seduc"
            })
            return resposta, contexto

        elif etapa == "aguarda_servico":
            opcao = mensagem.strip()
            if opcao not in ["1", "2", "3", "4"]:
                resposta = "Opção inválida. Por favor, selecione entre 1, 2, 3 ou 4."
                return resposta, contexto

            contexto["servico_selecionado"] = opcao

            if opcao == "3":  # vagas escolares
                resposta = "Certo! E de que cidade tu falas?"
                contexto["etapa"] = "aguarda_cidade_vagas"
            else:  # histórico, comprovante matrícula ou rematrícula
                resposta = mensagem_lgpd()
                contexto["etapa"] = "aguarda_consentimento_lgpd"
            return resposta, contexto

        elif etapa == "aguarda_cidade_vagas":
            cidade = mensagem.strip().title()
            contexto["cidade"] = cidade

            if cidade not in vagas_cidades:
                resposta = (
                    f"Desculpe, não tenho informações de vagas para a cidade {cidade}.\n"
                    "Por favor, informe uma cidade válida ou digite 'menu' para voltar."
                )
                return resposta, contexto
            else:
                resposta = (
                    f"Qual o tipo de ensino?\n"
                    f"1 - Infantil\n"
                    f"2 - Fundamental\n"
                    f"3 - Médio\n"
                    "Digite o número correspondente."
                )
                contexto["etapa"] = "aguarda_tipo_ensino"
                return resposta, contexto

        elif etapa == "aguarda_tipo_ensino":
            tipos = {"1": "infantil", "2": "fundamental", "3": "medio"}
            opcao = mensagem.strip()

            if opcao not in tipos:
                resposta = "Opção inválida. Por favor, selecione 1, 2 ou 3."
                return resposta, contexto

            cidade = contexto.get("cidade")
            tipo = tipos[opcao]
            vagas = vagas_cidades.get(cidade, {}).get(tipo, [])

            if not vagas:
                resposta = f"Não há vagas disponíveis para ensino {tipo} em {cidade} no momento."
            else:
                lista_vagas = "\n".join(f"• {vaga}" for vaga in vagas)
                resposta = (
                    f"Vagas disponíveis para ensino {tipo} em {cidade}:\n{lista_vagas}\n\n"
                    "Se quiser consultar outra cidade ou serviço, digite a consulta ou 'menu' para sair."
                )
            contexto["etapa"] = "pos_consulta"
            return resposta, contexto

        elif etapa == "aguarda_consentimento_lgpd":
            resposta_usuario = mensagem.strip().lower()
            if resposta_usuario not in ["sim", "não"]:
                resposta = "Por favor, responda 'sim' para concordar ou 'não' para cancelar."
                return resposta, contexto
            elif resposta_usuario == "não":
                resposta = "Entendido, não podemos continuar sem o seu consentimento. Se precisar de algo mais, é só chamar!"
                contexto = {"stage": "final"}
                return resposta, contexto
            else:
                resposta = "Ótimo! Por favor, informe seu nome completo, CPF e email separados por vírgula."
                contexto["etapa"] = "aguarda_dados_contato"
                return resposta, contexto

        elif etapa == "aguarda_dados_contato":
            dados = [d.strip() for d in mensagem.split(",")]
            if len(dados) < 3:
                resposta = "Por favor, informe nome completo, CPF e email separados por vírgula."
                return resposta, contexto

            nome, cpf, email = dados[0], dados[1], dados[2]
            contexto.update({"nome": nome, "cpf": cpf, "email": email})

            resposta = "Ok, estou buscando no sistema as informações para você..."
            contexto["etapa"] = "aguarda_confirmacao_resumo"
            return resposta, contexto

        elif etapa == "aguarda_confirmacao_resumo":
            # Simular resposta com dados fictícios
            nome = contexto.get("nome", "")
            cpf = contexto.get("cpf", "")
            resposta = (
                f"Confirme os dados:\nNome: {nome}\nCPF: {cpf}\nInstituição de Ensino São Judas Tadeu\nAno de conclusão: 2023\n\n"
                "Está tudo certo? (sim/não)"
            )
            contexto["etapa"] = "aguarda_confirmacao_usuario"
            return resposta, contexto

        elif etapa == "aguarda_confirmacao_usuario":
            resposta_usuario = mensagem.strip().lower()
            if resposta_usuario not in ["sim", "não"]:
                return "Por favor, responda 'sim' para confirmar ou 'não' para cancelar.", contexto
            if resposta_usuario == "não":
                contexto["etapa"] = "aguarda_dados_contato"
                return "Por favor, informe novamente seu nome completo, CPF e email separados por vírgula.", contexto

            resposta = (
                "Estamos enviando o PDF para o seu email. Se precisar de algo mais, estou à disposição!"
            )
            contexto = {"stage": "final"}
            return resposta, contexto

        elif etapa == "pos_consulta":
            msg_lower = mensagem.strip().lower()
            if msg_lower in ["menu", "voltar", "sair", "cancelar"]:
                resposta = "Consulta encerrada. Se precisar de algo mais, estou à disposição! 😊"
                contexto = {"stage": "final"}
                return resposta, contexto
            else:
                resposta = "Por favor, digite o número da opção que deseja ou 'menu' para sair."
                return resposta, contexto

        else:
            resposta = "Não entendi sua solicitação. Por favor, informe a opção desejada."
            contexto["etapa"] = "inicio"
            return resposta, contexto

    except Exception as e:
        logger.error(f"Erro no agente SEDUC: {str(e)}")
        return (
            "❌ Ocorreu um erro no atendimento SEDUC. Por favor, tente novamente.",
            {"stage": "final"},
        )
