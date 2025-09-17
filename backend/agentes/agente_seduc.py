import logging

logger = logging.getLogger(__name__)

def agente_seduc(mensagem, contexto=None):
    try:
        logger.debug(f"Agente SEDUC chamado - Mensagem: '{mensagem}', Contexto: {contexto}")
        
        if contexto is None:
            contexto = {}

        etapa = contexto.get("etapa", "inicio")
        logger.debug(f"Etapa atual: {etapa}")

        # Mocks simples para teste
        vagas_cidades = {
            "Porto Alegre": ["Escola Estadual A", "Escola Estadual B"],
            "Novo Hamburgo": ["Escola Estadual NH1", "Escola Estadual NH2"],
            "Canoas": ["Escola Estadual C1", "Escola Estadual C2"],
            "Caxias do Sul": ["Escola Estadual CS1", "Escola Estadual CS2"]
        }

        if etapa == "inicio":
            resposta = (
                "🏫 **SEDUC - Secretaria da Educação**\n\n"
                "Bem-vindo ao atendimento SEDUC!\n"
                "Por favor, informe sua cidade para continuar."
            )
            contexto.update({
                "etapa": "aguarde_cidade",
                "agente_ativo": "seduc"
            })
            logger.debug("Etapa definida como 'aguarde_cidade'")
            return resposta, contexto

        elif etapa == "aguarde_cidade":
            cidade = mensagem.strip().title()
            logger.debug(f"Cidade informada: {cidade}")
            
            contexto.update({
                "cidade": cidade,
                "etapa": "aguarde_servico",
                "agente_ativo": "seduc"
            })
            
            resposta = (
                f"📍 Cidade **{cidade}** selecionada.\n\n"
                "Escolha o serviço que deseja:\n\n"
                "**1** - Comprovante de matrícula\n"
                "**2** - Histórico escolar\n"
                "**3** - Vagas escolares disponíveis\n"
                "**4** - Rematrícula\n\n"
                "Digite o **número** da opção desejada."
            )
            return resposta, contexto

        elif etapa == "aguarde_servico":
            escolha = mensagem.lower().strip()
            cidade = contexto.get("cidade", "sua cidade")
            logger.debug(f"Escolha do serviço: {escolha}")

            if escolha == "1":
                resposta = (
                    f"📄 **Comprovante de Matrícula - {cidade}**\n\n"
                    "Para solicitar o comprovante de matrícula:\n"
                    "• Acesse o portal da SEDUC\n"
                    "• Ou envie um e-mail para: matricula@seduc.rs.gov.br\n"
                    "• Tenha em mãos: CPF do aluno e dados da escola\n\n"
                    "Posso ajudar com outro serviço? Digite o número correspondente ou 'menu' para voltar."
                )
            elif escolha == "2":
                resposta = (
                    f"📋 **Histórico Escolar - {cidade}**\n\n"
                    "Para obter o histórico escolar:\n"
                    "• Entre em contato com a escola onde foi matriculado\n"
                    "• Para escolas extintas: procure a Coordenadoria Regional de Educação\n"
                    "• Documentos necessários: RG e CPF do interessado\n\n"
                    "Digite outra opção ou 'menu' para voltar."
                )
            elif escolha == "3":
                vagas = vagas_cidades.get(cidade, [])
                if vagas:
                    lista_vagas = "• " + "\n• ".join(vagas)
                    resposta = (
                        f"🏫 **Vagas Disponíveis em {cidade}**\n\n"
                        f"{lista_vagas}\n\n"
                        "Para mais informações, entre em contato com a escola de interesse.\n"
                        "Digite outra opção ou 'menu' para voltar."
                    )
                else:
                    resposta = (
                        f"❌ Não há informações sobre vagas escolares disponíveis para **{cidade}** no momento.\n\n"
                        "Recomendamos entrar em contato com a Coordenadoria Regional de Educação.\n"
                        "Digite outra opção ou 'menu' para voltar."
                    )
            elif escolha == "4":
                resposta = (
                    f"🔄 **Rematrícula - {cidade}**\n\n"
                    "Para rematrícula:\n"
                    "• Verifique os prazos no portal da SEDUC\n"
                    "• Geralmente ocorre entre novembro e dezembro\n"
                    "• Acompanhe o calendário escolar oficial\n\n"
                    "Precisa de mais alguma coisa? Digite o número ou 'menu'."
                )
            elif escolha in ["sair", "cancelar", "menu", "voltar"]:
                resposta = (
                    "✅ Encerrando o atendimento SEDUC.\n"
                    "Se precisar de algo mais, é só chamar novamente! 😊"
                )
                contexto = {"stage": "final"}
                logger.debug("Finalizando agente SEDUC")
                return resposta, contexto
            else:
                resposta = (
                    "❌ Opção inválida.\n\n"
                    "Digite:\n"
                    "**1, 2, 3 ou 4** para os serviços\n"
                    "**'menu'** para voltar ao início"
                )
                return resposta, contexto

            # Manter na mesma etapa para permitir nova escolha
            contexto.update({
                "etapa": "aguarde_servico",
                "agente_ativo": "seduc"
            })
            return resposta, contexto

        else:
            logger.warning(f"Etapa desconhecida: {etapa}")
            resposta = (
                "❓ Desculpe, houve um problema na conversa.\n"
                "Vamos recomeçar: por favor, informe sua cidade para continuar."
            )
            contexto.update({
                "etapa": "aguarde_cidade",
                "agente_ativo": "seduc"
            })
            return resposta, contexto

    except Exception as e:
        logger.error(f"Erro no agente SEDUC: {str(e)}")
        return (
            "❌ Ocorreu um erro no atendimento SEDUC.\n"
            "Por favor, tente novamente ou digite 'menu' para voltar ao início."
        ), {"stage": "final"}