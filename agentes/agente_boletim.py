def agente_boletim(mensagem, contexto=None):
    """
    Agente para registrar boletim online ou indicar atendimento presencial,
    com suporte a contexto para controle de etapas e mensagem LGPD.
    """

    if contexto is None:
        contexto = {}

    stage = contexto.get("stage", "start")

    if stage == "start":
        resposta = (
            "Você deseja registrar boletim online ou atendimento presencial?\n"
            "1. Registrar boletim online\n"
            "2. Atendimento presencial (indicar delegacias)"
        )
        contexto["stage"] = "escolha_tipo"

    elif stage == "escolha_tipo":
        escolha = mensagem.strip()
        if escolha == "1":
            resposta = (
                "Antes de prosseguir com o registro do boletim online, "
                "você precisa aceitar nossa política de proteção de dados (LGPD). Você aceita? (sim/não)"
            )
            contexto["stage"] = "aguarda_lgpd_online"

        elif escolha == "2":
            resposta = "Informe a cidade onde deseja atendimento presencial."
            contexto["stage"] = "aguarda_cidade_presencial"

        else:
            resposta = "Opção inválida. Por favor, escolha 1 ou 2."

    elif stage == "aguarda_lgpd_online":
        if mensagem.lower() in ["sim", "aceito"]:
            resposta = "Para registrar o boletim online, por favor informe seu nome completo."
            contexto["stage"] = "aguarda_nome_online"
        else:
            resposta = "Não podemos prosseguir sem consentimento da LGPD."

    elif stage == "aguarda_nome_online":
        contexto["nome"] = mensagem.strip()
        resposta = "Obrigado. Agora por favor informe seu CPF."
        contexto["stage"] = "aguarda_cpf_online"

    elif stage == "aguarda_cpf_online":
        contexto["cpf"] = mensagem.strip()
        resposta = (
            "Você pode acessar o site https://www.delegaciaonline.rs.gov.br/dol/#!/index/main "
            "para continuar o registro do boletim online.\n"
            "Precisa de ajuda para usar o site?"
        )
        contexto["stage"] = "final"

    elif stage == "aguarda_cidade_presencial":
        contexto["cidade"] = mensagem.strip()
        # Simulação de consulta de delegacias
        resposta = (
            f"Delegacias disponíveis na cidade {contexto['cidade']}:\n"
            "- Delegacia Central - Endereço 123\n"
            "- Delegacia Norte - Endereço 456\n"
            "Deseja o endereço ou telefone de alguma delegacia? Informe o nome ou 'não'."
        )
        contexto["stage"] = "aguarda_detalhe_delegacia"

    elif stage == "aguarda_detalhe_delegacia":
        escolha = mensagem.strip().lower()
        if escolha in ["delegacia central", "delegacia norte"]:
            resposta = (
                f"Delegacia {escolha.title()}:\n"
                "Endereço: Rua Exemplo, 123\n"
                "Telefone: (51) 1234-5678\n"
                "Horário: 8h às 18h\n"
                "Precisa de ajuda para agendar atendimento?"
            )
            contexto["stage"] = "final"
        elif escolha in ["não", "nao"]:
            resposta = "Ok. Se precisar de mais informações, só chamar."
            contexto["stage"] = "final"
        else:
            resposta = "Não entendi. Por favor, informe o nome exato da delegacia ou 'não'."

    elif stage == "final":
        resposta = "Obrigado por usar os serviços do RSGOV. Se precisar de algo mais, é só chamar."

    else:
        resposta = "Não entendi sua solicitação. Tente novamente, por favor."

    return resposta, contexto
