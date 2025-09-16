from datetime import datetime, timedelta
import random

# --- Mensagem LGPD centralizada ---
def mensagem_lgpd():
    return (
        "⚠️ *Aviso de Privacidade (LGPD)*\n\n"
        "Para continuar, precisamos coletar e tratar alguns dados pessoais "
        "como nome, CPF e documentos. Esses dados serão utilizados *exclusivamente* "
        "para realizar o serviço solicitado.\n\n"
        "As informações serão tratadas conforme a Lei Geral de Proteção de Dados (Lei nº 13.709/2018), "
        "com segurança e confidencialidade.\n\n"
        "👉 Você concorda com o uso dos seus dados para essa finalidade? (sim/não)"
    )

# --- Locais específicos de Porto Alegre ---
def obter_locais_porto_alegre():
    return [
        {"id": "1", "nome": "Shopping João Pessoa", "endereco": "Av. João Pessoa 1831, 2º andar"},
        {"id": "2", "nome": "Unidade Azenha", "endereco": "Avenida Azenha, 255, Bairro Azenha"},
        {"id": "3", "nome": "Tudo Fácil Zona Sul", "endereco": "Av. Wenceslau Escobar, 2666 - bairro Tristeza"},
        {"id": "4", "nome": "Tudo Fácil Zona Norte", "endereco": "Av. Assis Brasil, 2611, 3º andar - Shopping Bourbon Wallig - bairro Cristo Redentor"},
        {"id": "5", "nome": "Tudo Fácil Centro", "endereco": "Av. Júlio de Castilhos, 235 - 3º andar do Pop Center"}
    ]

# --- Gerar próximos 7 dias úteis com horários ---
def gerar_datas_horarios():
    dias_uteis = []
    horarios = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
    data_atual = datetime.now()
    
    dias_adicionados = 0
    contador_dias = 1
    
    while dias_adicionados < 7:
        data_teste = data_atual + timedelta(days=contador_dias)
        # Segunda a sexta (0=segunda, 6=domingo)
        if data_teste.weekday() < 5:  # 0-4 são segunda a sexta
            data_formatada = data_teste.strftime("%d/%m")
            horarios_disponiveis = random.sample(horarios, k=random.randint(3, 5))
            horarios_disponiveis.sort()
            
            dias_uteis.append({
                "data": data_formatada,
                "data_completa": data_teste.strftime("%d/%m/%Y"),
                "horarios": horarios_disponiveis
            })
            dias_adicionados += 1
        contador_dias += 1
    
    return dias_uteis

def agente_identidade(mensagem, contexto=None):
    if contexto is None:
        contexto = {}

    stage = contexto.get("stage", "start")
    resposta = "Não entendi sua solicitação. Poderia reformular?"  # Resposta padrão

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
                "1. **Identidade Fácil**\n"
                "2. **Agendamento Presencial**\n\n"
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
        if escolha_modalidade == "1":  # Identidade Fácil
            resposta = (
                "Você escolheu **Identidade Fácil**. Para este serviço, você precisará ter em mãos:\n"
                "- Certidão de Nascimento (para solteiros) ou Casamento (para casados/divorciados).\n"
                "- CPF.\n\n"
                "Você possui estes documentos? (sim/não)"
            )
            contexto["stage"] = "ifacil_docs"
        elif escolha_modalidade == "2":  # Agendamento Presencial
            resposta = mensagem_lgpd()
            contexto["stage"] = "presencial_lgpd"
        else:
            resposta = "Opção inválida. Por favor, escolha 1 para Identidade Fácil ou 2 para Agendamento Presencial."

    # --- RAMO 1: FLUXO IDENTIDADE FÁCIL ---
    elif stage == "ifacil_docs":
        if mensagem.lower().strip() == "sim":
            resposta = mensagem_lgpd()
            contexto["stage"] = "ifacil_lgpd"
        else:
            resposta = "Sem os documentos necessários, não é possível seguir com o Identidade Fácil. Gostaria de tentar o Agendamento Presencial? (sim/não)"
            contexto["stage"] = "ifacil_sem_docs_redirect"

    elif stage == "ifacil_sem_docs_redirect":
        if mensagem.lower().strip() == "sim":
            resposta = mensagem_lgpd()
            contexto["stage"] = "presencial_lgpd"
        else:
            resposta = "Entendido. Processo encerrado. Se precisar de algo mais, é só chamar."
            contexto["stage"] = "final"

    elif stage == "ifacil_lgpd":
        if mensagem.lower().strip() == "sim":
            resposta = "Por favor, informe seu nome completo."
            contexto["stage"] = "aguarda_nome"
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
        cidade = mensagem.strip().lower()
        contexto["cidade"] = mensagem.strip()
        
        # Verificar se é Porto Alegre
        if "porto alegre" in cidade or "poa" in cidade:
            locais = obter_locais_porto_alegre()
            resposta_locais = f"Encontrei os seguintes postos em **{contexto['cidade']}**:\n\n"
            for local in locais:
                resposta_locais += f"{local['id']}. {local['nome']}\n   📍 {local['endereco']}\n\n"
            resposta_locais += "Por favor, digite o número do local desejado."
            resposta = resposta_locais
            contexto["locais_disponiveis"] = locais
            contexto["stage"] = "presencial_escolhe_local"
        else:
            resposta = (
                f"Desculpe, não encontrei postos disponíveis em **{contexto['cidade']}** no momento. "
                "Tente uma cidade próxima ou entre em contato conosco para mais informações."
            )
            contexto["stage"] = "final"

    elif stage == "presencial_escolhe_local":
        escolha = mensagem.strip()
        locais = contexto.get("locais_disponiveis", [])
        
        try:
            local_selecionado = next(local for local in locais if local["id"] == escolha)
            contexto["local_escolhido"] = local_selecionado
            
            # Gerar datas e horários
            datas_horarios = gerar_datas_horarios()
            contexto["datas_disponiveis"] = datas_horarios
            
            resposta = f"**{local_selecionado['nome']}**\n📍 {local_selecionado['endereco']}\n\n"
            resposta += "📅 **Datas e horários disponíveis:**\n\n"
            
            for i, dia in enumerate(datas_horarios[:5], 1):  # Mostrar apenas 5 primeiros dias
                resposta += f"{i}. **{dia['data']}** - "
                resposta += ", ".join(dia['horarios'][:3])  # Mostrar 3 horários por linha
                resposta += "\n"
            
            resposta += "\nDigite o número da data desejada."
            contexto["stage"] = "presencial_escolhe_data"
            
        except (StopIteration, ValueError):
            resposta = "Opção inválida. Por favor, digite um número válido do local."

    elif stage == "presencial_escolhe_data":
        try:
            escolha = int(mensagem.strip())
            datas_disponiveis = contexto.get("datas_disponiveis", [])
            
            if 1 <= escolha <= len(datas_disponiveis):
                data_selecionada = datas_disponiveis[escolha - 1]
                contexto["data_selecionada"] = data_selecionada
                
                resposta = f"📅 **Data selecionada: {data_selecionada['data']}**\n\n"
                resposta += "🕐 **Horários disponíveis:**\n\n"
                
                for i, horario in enumerate(data_selecionada['horarios'], 1):
                    resposta += f"{i}. {horario}\n"
                
                resposta += "\nDigite o número do horário desejado."
                contexto["stage"] = "presencial_escolhe_horario"
            else:
                resposta = "Opção inválida. Por favor, digite um número válido da data."
                
        except ValueError:
            resposta = "Por favor, digite apenas o número da data desejada."

    elif stage == "presencial_escolhe_horario":
        try:
            escolha = int(mensagem.strip())
            data_selecionada = contexto.get("data_selecionada", {})
            horarios = data_selecionada.get("horarios", [])
            
            if 1 <= escolha <= len(horarios):
                horario_selecionado = horarios[escolha - 1]
                contexto["horario_selecionado"] = horario_selecionado
                
                resposta = (
                    "✅ **Confirmação do Agendamento:**\n\n"
                    f"📍 **Local:** {contexto['local_escolhido']['nome']}\n"
                    f"🏢 **Endereço:** {contexto['local_escolhido']['endereco']}\n"
                    f"🏙️ **Cidade:** {contexto['cidade']}\n"
                    f"📅 **Data:** {data_selecionada['data']}\n"
                    f"🕐 **Horário:** {horario_selecionado}\n\n"
                    "Está tudo correto? Posso confirmar? (sim/não)"
                )
                contexto["stage"] = "presencial_finaliza"
            else:
                resposta = "Opção inválida. Por favor, digite um número válido do horário."
                
        except ValueError:
            resposta = "Por favor, digite apenas o número do horário desejado."

    elif stage == "presencial_finaliza":
        if mensagem.lower().strip() == "sim":
            protocolo = f"PRESENCIAL-{random.randint(10000, 99999)}"
            resposta = (
                f"🎉 **Agendamento confirmado com sucesso!**\n\n"
                f"📋 **Protocolo:** {protocolo}\n"
                f"📧 Um comprovante em PDF será enviado para seu e-mail.\n\n"
                f"📍 **Lembre-se:**\n"
                f"• Local: {contexto['local_escolhido']['nome']}\n"
                f"• Data: {contexto['data_selecionada']['data']}\n"
                f"• Horário: {contexto['horario_selecionado']}\n\n"
                f"⚠️ Chegue com 15 minutos de antecedência."
            )
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
        cidade = mensagem.strip().lower()
        contexto["cidade_ifacil"] = mensagem.strip()
        
        if "porto alegre" in cidade or "poa" in cidade:
            locais = obter_locais_porto_alegre()
            resposta_locais = f"Ótimo. Para **{contexto['cidade_ifacil']}**, temos os seguintes postos de atendimento:\n\n"
            for local in locais[:5]:  #
                resposta_locais += f"{local['id']}. {local['nome']}\n   📍 {local['endereco']}\n\n"
            resposta_locais += "Por favor, digite o número do local desejado."
            resposta = resposta_locais
            contexto["locais_ifacil"] = locais[:5]
            contexto["stage"] = "ifacil_escolhe_local"
        else:
            resposta = f"Desculpe, o Identidade Fácil não está disponível em **{contexto['cidade_ifacil']}** no momento."
            contexto["stage"] = "final"

    elif stage == "ifacil_escolhe_local":
        escolha = mensagem.strip()
        locais = contexto.get("locais_ifacil", [])
        
        try:
            local_selecionado = next(local for local in locais if local["id"] == escolha)
            contexto["local_ifacil"] = local_selecionado
            
            datas_horarios = gerar_datas_horarios()
            contexto["datas_ifacil"] = datas_horarios
            
            resposta = f"**{local_selecionado['nome']}**\n📍 {local_selecionado['endereco']}\n\n"
            resposta += "📅 **Datas e horários disponíveis:**\n\n"
            
            for i, dia in enumerate(datas_horarios[:3], 1):
                resposta += f"{i}. **{dia['data']}** - "
                resposta += ", ".join(dia['horarios'][:3])
                resposta += "\n"
            
            resposta += "\nDigite o número da data desejada."
            contexto["stage"] = "ifacil_escolhe_data"
            
        except (StopIteration, ValueError):
            resposta = "Opção inválida. Por favor, digite um número válido do local."

    elif stage == "ifacil_escolhe_data":
        try:
            escolha = int(mensagem.strip())
            datas_disponiveis = contexto.get("datas_ifacil", [])
            
            if 1 <= escolha <= len(datas_disponiveis):
                data_selecionada = datas_disponiveis[escolha - 1]
                contexto["data_ifacil_selecionada"] = data_selecionada
                
                resposta = f"📅 **Data selecionada: {data_selecionada['data']}**\n\n"
                resposta += "🕐 **Horários disponíveis:**\n\n"
                
                for i, horario in enumerate(data_selecionada['horarios'], 1):
                    resposta += f"{i}. {horario}\n"
                
                resposta += "\nDigite o número do horário desejado."
                contexto["stage"] = "ifacil_escolhe_horario"
            else:
                resposta = "Opção inválida. Por favor, digite um número válido da data."
                
        except ValueError:
            resposta = "Por favor, digite apenas o número da data desejada."

    elif stage == "ifacil_escolhe_horario":
        try:
            escolha = int(mensagem.strip())
            data_selecionada = contexto.get("data_ifacil_selecionada", {})
            horarios = data_selecionada.get("horarios", [])
            
            if 1 <= escolha <= len(horarios):
                horario_selecionado = horarios[escolha - 1]
                contexto["horario_ifacil_selecionado"] = horario_selecionado
                
                resposta = (
                    "✅ **Confirmação do Agendamento - Identidade Fácil:**\n\n"
                    f"📍 **Local:** {contexto['local_ifacil']['nome']}\n"
                    f"🏢 **Endereço:** {contexto['local_ifacil']['endereco']}\n"
                    f"🏙️ **Cidade:** {contexto['cidade_ifacil']}\n"
                    f"📅 **Data:** {data_selecionada['data']}\n"
                    f"🕐 **Horário:** {horario_selecionado}\n\n"
                    "Posso confirmar? (sim/não)"
                )
                contexto["stage"] = "ifacil_finaliza"
            else:
                resposta = "Opção inválida. Por favor, digite um número válido do horário."
                
        except ValueError:
            resposta = "Por favor, digite apenas o número do horário desejado."

    elif stage == "ifacil_finaliza":
        if mensagem.lower().strip() in ["sim", "confirmo"]:
            protocolo = f"RS-ID-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            resposta = (
                f"🎉 **Agendamento via Identidade Fácil realizado com sucesso!**\n\n"
                f"📋 **Protocolo:** {protocolo}\n"
                f"📧 As instruções para a etapa presencial foram enviadas para seu e-mail.\n\n"
                f"📍 **Lembre-se:**\n"
                f"• Local: {contexto['local_ifacil']['nome']}\n"
                f"• Data: {contexto['data_ifacil_selecionada']['data']}\n"
                f"• Horário: {contexto['horario_ifacil_selecionado']}\n\n"
                f"⚠️ Chegue com 15 minutos de antecedência e traga os documentos originais."
            )
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
                "1. Agendamento em SHOPPING JOÃO PESSOA dia 20/09 às 10:00\n"
                "2. Agendamento em TUDO FÁCIL ZONA SUL dia 22/09 às 14:00\n"
                f"Digite o número do agendamento para {'ver detalhes' if acao == '2' else 'cancelar'}."
            )
            contexto["stage"] = "escolhe_agendamento_cancelar" if acao == "4" else "escolhe_agendamento"
            contexto["agendamentos"] = [
                {"id": "1", "local": "SHOPPING JOÃO PESSOA", "data": "20/09", "hora": "10:00"},
                {"id": "2", "local": "TUDO FÁCIL ZONA SUL", "data": "22/09", "hora": "14:00"},
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
            contexto = {"stage": "start"}

    return resposta, contexto