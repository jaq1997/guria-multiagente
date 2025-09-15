from datetime import datetime, timedelta
import random

def agente_identidade(mensagem, contexto=None):
    if contexto is None:
        contexto = {}

    stage = contexto.get("stage", "start")
    resposta = "Não entendi sua solicitação. Poderia reformular?" # Resposta padrão

    if stage == "start":
        resposta = (
            "Certo, sobre a **Carteira de Identidade**. Eu posso te ajudar com as seguintes opções:\n\n"
            "1. Agendar 2ª via\n"
            "2. Consultar Agendamento\n"
            "3. Consultar Andamento\n"
            "4. Cancelar Agendamento\n\n"
            "Por favor, digite o número da opção desejada."
        )
        contexto["stage"] = "aguarda_escolha"
    
    elif stage == "aguarda_escolha":
        escolha = mensagem.strip()
        if escolha == "1":
            resposta = (
                "Entendido. Para a 2ª via da Identidade, você gostaria de seguir com qual modalidade?\n\n"
                "1. **Identidade Fácil** (serviço online híbrido)\n"
                "2. **Agendamento Presencial** (atendimento em um posto do IGP)\n\n"
                "Por favor, digite o número da opção."
            )
            contexto["stage"] = "aguarda_modalidade_2via"
        elif escolha in ["2", "3", "4"]:
            contexto["acao"] = escolha
            resposta = "Por favor, informe seu CPF ou o código de protocolo do agendamento."
            contexto["stage"] = "aguarda_cpf_protocolo"
        else:
            resposta = "Opção inválida. Por favor, digite 1, 2, 3 ou 4."

    elif stage == "aguarda_modalidade_2via":
        escolha_modalidade = mensagem.strip()
        if escolha_modalidade == "1": # Identidade Fácil
            resposta = (
                "Você escolheu **Identidade Fácil**. Para este serviço, você precisará ter em mãos:\n"
                "- Certidão de Nascimento (para solteiros) ou Casamento (para casados/divorciados).\n"
                "- CPF.\n\n"
                "Você possui estes documentos? (sim/não)"
            )
            contexto["stage"] = "ifacil_docs"
        elif escolha_modalidade == "2": # Agendamento Presencial
            resposta = (
                "Você escolheu **Agendamento Presencial**. Para prosseguir, preciso do seu consentimento para coletar alguns dados pessoais, conforme a LGPD. Você concorda? (sim/não)"
            )
            contexto["stage"] = "presencial_lgpd"
        else:
            resposta = "Opção inválida. Por favor, escolha 1 para Identidade Fácil ou 2 para Agendamento Presencial."

    # --- RAMO 1: FLUXO IDENTIDADE FÁCIL ---
    elif stage == "ifacil_docs":
        if mensagem.lower().strip() == "sim":
            resposta = "Ótimo. Para continuar com o Identidade Fácil, preciso do seu consentimento para uso dos dados, conforme a LGPD. Você concorda? (sim/não)"
            contexto["stage"] = "ifacil_lgpd"
        else:
            resposta = "Sem os documentos necessários, não é possível seguir com o Identidade Fácil. Gostaria de tentar o Agendamento Presencial? (sim/não)"
            contexto["stage"] = "ifacil_sem_docs_redirect"
    
    elif stage == "ifacil_sem_docs_redirect":
        if mensagem.lower().strip() == "sim":
            resposta = "Ok. Para o **Agendamento Presencial**, preciso do seu consentimento para coletar dados pessoais, conforme a LGPD. Você concorda? (sim/não)"
            contexto["stage"] = "presencial_lgpd"
        else:
            resposta = "Entendido. Processo encerrado. Se precisar de algo mais, é só chamar."
            contexto["stage"] = "final"

    elif stage == "ifacil_lgpd":
        if mensagem.lower().strip() == "sim":
            resposta = "Por favor, informe seu nome completo."
            contexto["stage"] = "aguarda_nome" # Reutiliza o fluxo de coleta de dados
        else:
            resposta = "Não podemos prosseguir sem consentimento da LGPD. Processo encerrado."
            contexto["stage"] = "final"

    # --- RAMO 2: FLUXO AGENDAMENTO PRESENCIAL ---
    elif stage == "presencial_lgpd":
        if mensagem.lower().strip() == "sim":
            resposta = "Obrigado. Por favor, informe a cidade onde você gostaria de ser atendido(a)."
            contexto["stage"] = "presencial_cidade"
        else:
            resposta = "Não podemos prosseguir sem consentimento da LGPD. Processo encerrado."
            contexto["stage"] = "final"

    elif stage == "presencial_cidade":
        cidade = mensagem.strip()
        contexto["cidade"] = cidade
        resposta = (
            f"Encontrei os seguintes postos em **{cidade}**:\n"
            "1. Posto IGP - TudoFácil Zona Sul\n"
            "2. Posto IGP - Azenha\n\n"
            "Por favor, escolha o local de atendimento."
        )
        contexto["stage"] = "presencial_escolhe_local"

    elif stage == "presencial_escolhe_local":
        escolha = mensagem.strip()
        horarios = ["10:00", "11:00", "14:00", "15:00"]
        random.shuffle(horarios)
        data_amanha = datetime.now() + timedelta(days=1)
        data_formatada = data_amanha.strftime("%d/%m/%Y")
        resposta = (
            f"Para o local escolhido, temos os seguintes horários disponíveis para amanhã ({data_formatada}):\n"
            f"1. {horarios[0]}\n"
            f"2. {horarios[1]}\n"
            f"3. {horarios[2]}\n\n"
            "Qual horário você prefere?"
        )
        contexto["local_escolhido"] = "Posto IGP - TudoFácil Zona Sul" if escolha == "1" else "Posto IGP - Azenha"
        contexto["data_agendamento"] = data_formatada
        contexto["stage"] = "presencial_confirma"
    
    elif stage == "presencial_confirma":
        horario_escolhido = "10:00" 
        contexto["horario_escolhido"] = horario_escolhido
        resposta = (
            "Ótimo! Vamos confirmar seu agendamento:\n\n"
            f"Local: {contexto.get('local_escolhido')}\n"
            f"Cidade: {contexto.get('cidade')}\n"
            f"Data: {contexto.get('data_agendamento')}\n"
            f"Horário: {contexto.get('horario_escolhido')}\n\n"
            "Está tudo certo? Posso confirmar? (sim/não)"
        )
        contexto["stage"] = "presencial_finaliza"
        
    elif stage == "presencial_finaliza":
        if mensagem.lower().strip() == "sim":
            protocolo = f"PRESENCIAL-{random.randint(10000, 99999)}"
            resposta = f"Agendamento presencial confirmado com sucesso! Seu protocolo é **{protocolo}**. Um comprovante em PDF será enviado para seu e-mail."
        else:
            resposta = "Agendamento cancelado. Se precisar, podemos recomeçar."
        contexto["stage"] = "final"

    # --- FLUXO DE COLETA DE DADOS (USADO PELO IDENTIDADE FÁCIL) ---
    elif stage == "aguarda_nome":
        nome_completo = mensagem.strip()
        contexto["nome_completo"] = nome_completo
        primeiro_nome = nome_completo.split(' ')[0]
        resposta = f"Obrigado, {primeiro_nome}. Agora, por favor, informe sua data de nascimento (no formato DD/MM/AAAA)."
        contexto["stage"] = "aguarda_nascimento"

    elif stage == "aguarda_nascimento":
        data_nasc_str = mensagem.strip()
        try:
            datetime.strptime(data_nasc_str, '%d/%m/%Y')
            contexto["data_nascimento"] = data_nasc_str
            resposta = "Ótimo. Agora, informe o nome completo da sua mãe."
            contexto["stage"] = "aguarda_nome_mae"
        except ValueError:
            resposta = "Formato de data inválido. Por favor, digite no formato DD/MM/AAAA (ex: 25/12/1990)."

    elif stage == "aguarda_nome_mae":
        nome_mae = mensagem.strip()
        contexto["nome_mae"] = nome_mae
        resposta = "Entendido. Por último, informe seu CPF (apenas números)."
        contexto["stage"] = "aguarda_cpf_agendamento"

    elif stage == "aguarda_cpf_agendamento":
        cpf = mensagem.strip().replace(".", "").replace("-", "")
        if cpf.isdigit() and len(cpf) == 11:
            contexto["cpf"] = cpf
            resposta = (
                "Perfeito! Por favor, confirme se os dados estão corretos:\n\n"
                f"Nome: {contexto.get('nome_completo')}\n"
                f"Data de Nascimento: {contexto.get('data_nascimento')}\n"
                f"Nome da Mãe: {contexto.get('nome_mae')}\n"
                f"CPF: {contexto.get('cpf')}\n\n"
                "Podemos confirmar os dados? (sim/não)"
            )
            contexto["stage"] = "confirma_dados"
        else:
            resposta = "CPF inválido. Por favor, digite um CPF válido com 11 números."
    
    # --- FLUXO COMBINADO: UPLOAD + AGENDAMENTO ---
    elif stage == "confirma_dados":
        if mensagem.lower().strip() in ["sim", "confirmo"]:
            resposta = (
                "Ótimo, dados confirmados. Agora, vamos para os documentos.\n\n"
                "Por favor, use o botão de clipe (📎) para anexar uma foto da sua **Certidão de Nascimento ou Casamento**. "
                "Após o envio, digite **'pronto'**."
            )
            contexto["stage"] = "aguarda_upload_certidao"
        else:
            resposta = "Ok, o processo foi cancelado. Se precisar recomeçar, é só chamar."
            contexto["stage"] = "final"
    
    elif stage == "aguarda_upload_certidao":
        if mensagem.lower().strip() in ["pronto", "ok", "enviei"]:
            documentos = contexto.get("documentos_enviados", [])
            if any("certidao" in doc.lower() or "casamento" in doc.lower() or "nascimento" in doc.lower() for doc in documentos):
                resposta = (
                    "Certidão recebida! Agora, por favor, envie uma foto do seu **CPF**.\n\n"
                    "Após o envio, digite **'pronto'**."
                )
                contexto["stage"] = "aguarda_upload_cpf"
            else:
                resposta = "Ainda não identifiquei o envio da sua certidão. Por favor, use o clipe (📎) para enviar o arquivo correto e depois digite 'pronto'."
        else:
            resposta = "Por favor, digite 'pronto' assim que terminar de enviar o anexo da certidão."

    elif stage == "aguarda_upload_cpf":
        if mensagem.lower().strip() in ["pronto", "ok", "enviei"]:
            documentos = contexto.get("documentos_enviados", [])
            if any("cpf" in doc.lower() for doc in documentos):
                resposta = "Documentos recebidos! Para finalizar, vamos encontrar um local para sua etapa presencial. Por favor, informe sua cidade."
                contexto["stage"] = "ifacil_pede_cidade"
            else:
                resposta = "Ainda não identifiquei o envio do seu CPF. Por favor, use o clipe (📎) para enviar e depois digite 'pronto'."
        else:
            resposta = "Por favor, digite 'pronto' assim que terminar de enviar o anexo do CPF."

    elif stage == "ifacil_pede_cidade":
        cidade = mensagem.strip()
        contexto["cidade_ifacil"] = cidade
        resposta = (
            f"Ótimo. Para **{cidade}**, temos os seguintes postos de atendimento:\n"
            "1. Posto Central\n"
            "2. Posto TudoFácil\n\n"
            "Por favor, digite o número do local desejado."
        )
        contexto["stage"] = "ifacil_escolhe_local"

    elif stage == "ifacil_escolhe_local":
        local_escolhido = "Posto Central" if mensagem.strip() == "1" else "Posto TudoFácil"
        contexto["local_ifacil"] = local_escolhido
        horarios = ["10:30", "11:30", "14:30"]
        data_amanha = datetime.now() + timedelta(days=1)
        data_formatada = data_amanha.strftime("%d/%m/%Y")
        resposta = (
            f"Para o **{local_escolhido}**, encontramos os seguintes horários disponíveis para amanhã ({data_formatada}):\n"
            f"1. {horarios[0]}\n"
            f"2. {horarios[1]}\n"
            f"3. {horarios[2]}\n\n"
            "Qual horário você prefere?"
        )
        contexto["stage"] = "ifacil_confirma_final"

    elif stage == "ifacil_confirma_final":
        horario_escolhido = "10:30"
        contexto["horario_ifacil"] = horario_escolhido
        data_agendamento = contexto.get('data_agendamento_ifacil', (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"))
        resposta = (
            "Perfeito! Revisando seu agendamento para a etapa presencial:\n\n"
            f"Local: {contexto.get('local_ifacil')}\n"
            f"Cidade: {contexto.get('cidade_ifacil')}\n"
            f"Data: {data_agendamento}\n"
            f"Horário: {horario_escolhido}\n\n"
            "Posso confirmar? (sim/não)"
        )
        contexto["stage"] = "ifacil_finaliza"

    elif stage == "ifacil_finaliza":
        if mensagem.lower().strip() in ["sim", "confirmo"]:
            protocolo = f"RS-ID-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            resposta = f"Agendamento via Identidade Fácil realizado com sucesso! Seu número de protocolo é **{protocolo}**. As instruções para a etapa presencial foram enviadas para seu e-mail."
        else:
            resposta = "Ok, o agendamento foi cancelado."
        contexto["stage"] = "final"


    # --- FLUXOS DE CONSULTA E CANCELAMENTO ---
    elif stage == "aguarda_cpf_protocolo":
        dado = mensagem.strip()
        contexto["cpf_protocolo"] = dado
        acao = contexto.get("acao")
        if acao in ["2", "4"]:
            resposta = (
                f"Encontramos os seguintes agendamentos para '{dado}':\n"
                "1. Agendamento em POSTO IGP - TUDOFÁCIL ZONA SUL dia 20/09 às 10h\n"
                "2. Agendamento em POSTO IGP - CACHOEIRINHA dia 22/09 às 14h\n"
                f"Digite o número do agendamento para {'ver detalhes' if acao == '2' else 'cancelar'}."
            )
            contexto["stage"] = "escolhe_agendamento_cancelar" if acao == "4" else "escolhe_agendamento"
            contexto["agendamentos"] = [
                {"id": "1", "local": "POSTO IGP - TUDOFÁCIL ZONA SUL", "data": "20/09", "hora": "10h"},
                {"id": "2", "local": "POSTO IGP - CACHOEIRINHA", "data": "22/09", "hora": "14h"},
            ]
        elif acao == "3":
            resposta = f"O andamento do seu protocolo '{dado}' é: **Em análise pela equipe do IGP.**"
            contexto["stage"] = "final"

    elif stage == "escolhe_agendamento":
        escolha = mensagem.strip()
        agendamentos = contexto.get("agendamentos", [])
        try:
            ag = agendamentos[int(escolha) - 1]
            resposta = f"Detalhes do agendamento:\nLocal: {ag['local']}\nData: {ag['data']}\nHora: {ag['hora']}"
            contexto["stage"] = "final"
        except (IndexError, ValueError):
            resposta = "Opção inválida. Por favor, digite o número correto do agendamento."

    elif stage == "escolhe_agendamento_cancelar":
        escolha = mensagem.strip()
        agendamentos = contexto.get("agendamentos", [])
        try:
            ag = agendamentos[int(escolha) - 1]
            resposta = f"Confirma o cancelamento do agendamento no local {ag['local']} dia {ag['data']} às {ag['hora']}? (sim/não)"
            contexto["escolha_agendamento_cancelar"] = ag
            contexto["stage"] = "confirma_cancelamento_final"
        except (IndexError, ValueError):
            resposta = "Opção inválida. Por favor, digite o número correto."

    elif stage == "confirma_cancelamento_final":
        if mensagem.lower().strip() in ["sim", "confirmo", "ok"]:
            ag = contexto.get("escolha_agendamento_cancelar")
            resposta = f"Agendamento no local {ag['local']} dia {ag['data']} às {ag['hora']} **cancelado com sucesso**."
        else:
            resposta = "Cancelamento abortado. Se precisar, é só chamar."
        contexto["stage"] = "final"

    else:
        if stage not in ["start", "final"]:
             resposta = "Não entendi. Por favor, tente novamente."
             contexto = {"agente_ativo": "identidade", "stage": "start"}

    return resposta, contexto