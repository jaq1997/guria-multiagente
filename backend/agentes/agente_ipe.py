import logging

logger = logging.getLogger(__name__)

def agente_ipe(mensagem, contexto=None):
    try:
        logger.debug(f"Agente IPE chamado - Mensagem: '{mensagem}', Contexto: {contexto}")
        
        if contexto is None:
            contexto = {}

        etapa = contexto.get("etapa", "inicio")
        logger.debug(f"Etapa atual: {etapa}")

        # Dados mock por cidade - para teste e exemplo
        estabelecimentos = {
            "Porto Alegre": [
                {"nome": "Hospital Moinhos de Vento", "tipo": "Hospital", "endereco": "Rua Ramiro Barcelos, 910", "telefone": "(51) 3314-3000"},
                {"nome": "Clínica Mãe de Deus", "tipo": "Clínica", "endereco": "Rua José de Alencar, 286", "telefone": "(51) 3230-3600"},
                {"nome": "Hospital de Clínicas", "tipo": "Hospital", "endereco": "Rua Ramiro Barcelos, 2350", "telefone": "(51) 3359-8000"}
            ],
            "Caxias do Sul": [
                {"nome": "Hospital Pompéia", "tipo": "Hospital", "endereco": "Rua Silveira Martins, 555", "telefone": "(54) 3218-8000"},
                {"nome": "Hospital Geral", "tipo": "Hospital", "endereco": "Rua Ernesto Alves, 1985", "telefone": "(54) 3290-8000"}
            ],
            "Canoas": [
                {"nome": "Hospital Universitário", "tipo": "Hospital", "endereco": "Av. Farroupilha, 8001", "telefone": "(51) 3612-1200"},
                {"nome": "Clínica São Vicente", "tipo": "Clínica", "endereco": "Rua Tiradentes, 235", "telefone": "(51) 3472-3456"}
            ]
        }

        if etapa == "inicio":
            resposta = (
                "🏥 **IPE Saúde - Rede Credenciada**\n\n"
                "Bem-vindo ao sistema de consulta de hospitais e clínicas credenciados!\n\n"
                "Por favor, informe sua **cidade** para que eu possa listar os estabelecimentos disponíveis."
            )
            contexto.update({
                "etapa": "aguarde_cidade",
                "agente_ativo": "ipe"
            })
            logger.debug("Etapa definida como 'aguarde_cidade'")
            return resposta, contexto

        elif etapa == "aguarde_cidade":
            cidade = mensagem.strip().title()
            logger.debug(f"Cidade informada: {cidade}")
            
            contexto.update({
                "cidade": cidade,
                "agente_ativo": "ipe"
            })

            lista_estabelecimentos = estabelecimentos.get(cidade)
            if not lista_estabelecimentos:
                resposta = (
                    f"❌ Desculpe, não tenho informações sobre estabelecimentos credenciados para **{cidade}**.\n\n"
                    "Cidades disponíveis:\n"
                    "• Porto Alegre\n"
                    "• Caxias do Sul\n"
                    "• Canoas\n\n"
                    "Por favor, informe uma das cidades acima ou digite 'menu' para voltar."
                )
                contexto["etapa"] = "aguarde_cidade"  # Manter na mesma etapa
                return resposta, contexto

            # Construir resposta com estabelecimentos
            resposta = f"🏥 **Estabelecimentos IPE Saúde em {cidade}**\n\n"
            
            hospitais = [e for e in lista_estabelecimentos if e['tipo'] == 'Hospital']
            clinicas = [e for e in lista_estabelecimentos if e['tipo'] == 'Clínica']
            
            if hospitais:
                resposta += "**🏥 HOSPITAIS:**\n"
                for e in hospitais:
                    resposta += f"• **{e['nome']}**\n"
                    resposta += f"  📍 {e['endereco']}\n"
                    resposta += f"  📞 {e['telefone']}\n\n"
            
            if clinicas:
                resposta += "**🏥 CLÍNICAS:**\n"
                for e in clinicas:
                    resposta += f"• **{e['nome']}**\n"
                    resposta += f"  📍 {e['endereco']}\n"
                    resposta += f"  📞 {e['telefone']}\n\n"

            resposta += (
                "ℹ️ **Informações importantes:**\n"
                "• Confirme sempre a cobertura antes da consulta\n"
                "• Tenha em mãos sua carteirinha do IPE\n"
                "• Para emergências, ligue 192 (SAMU)\n\n"
                "Precisa de informações sobre outra cidade? Digite o nome da cidade ou 'menu' para voltar."
            )
            
            contexto["etapa"] = "pos_consulta"
            logger.debug("Etapa definida como 'pos_consulta'")
            return resposta, contexto

        elif etapa == "pos_consulta":
            msg_lower = mensagem.lower().strip()
            
            if msg_lower in ["menu", "voltar", "sair", "cancelar"]:
                resposta = (
                    "✅ Encerrando consulta IPE Saúde.\n"
                    "Se precisar de algo mais, é só chamar! 😊"
                )
                contexto = {"stage": "final"}
                logger.debug("Finalizando agente IPE")
                return resposta, contexto
            
            # Se digitou outra cidade, processar
            cidade = mensagem.strip().title()
            contexto.update({
                "cidade": cidade,
                "etapa": "aguarde_cidade"
            })
            
            # Redirecionar para processar a nova cidade
            return agente_ipe(cidade, contexto)

        else:
            logger.warning(f"Etapa desconhecida: {etapa}")
            resposta = (
                "❓ Houve um problema na conversa.\n"
                "Por favor, informe sua cidade para consultar estabelecimentos credenciados."
            )
            contexto.update({
                "etapa": "aguarde_cidade",
                "agente_ativo": "ipe"
            })
            return resposta, contexto

    except Exception as e:
        logger.error(f"Erro no agente IPE: {str(e)}")
        return (
            "❌ Ocorreu um erro na consulta IPE Saúde.\n"
            "Por favor, tente novamente ou digite 'menu' para voltar ao início."
        ), {"stage": "final"}