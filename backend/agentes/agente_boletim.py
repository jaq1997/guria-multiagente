import random
from datetime import datetime


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


def mensagem_falso_crime():
    return (
        "⚠️ *Registro falso é Crime*\n\n"
        "A comunicação falsa de crime ou contravenção está sujeita às penas dos arts. 138, 339 e 340 do Código Penal Brasileiro."
        "\n\nVocê entendeu e está ciente? (sim/não)"
    )


def gerar_protocolo():
    return f"BO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100,999)}"


def agente_boletim(mensagem, contexto=None):
    if contexto is None:
        contexto = {}
    stage = contexto.get("stage", "start")
    resposta = ""

    if stage == "start":
        resposta = (
            "⚠️ *Importante*:\n"
            "O fato ocorrido fora do Estado do Rio Grande do Sul NÃO poderá ser registrado pela Delegacia Online.\n"
            "Nesses casos, o registro deverá ser feito presencialmente em qualquer Delegacia de Polícia.\n\n"
            "Você deseja registrar boletim online ou atendimento presencial?\n"
            "1. Registrar boletim online\n"
            "2. Atendimento presencial (indicar telefone de contato das delegacias)"
        )
        contexto["stage"] = "escolha_tipo"

    elif stage == "escolha_tipo":
        escolha = mensagem.strip()
        if escolha == "1":
            resposta = mensagem_lgpd()
            contexto["stage"] = "aguarda_lgpd_online"
        elif escolha == "2":
            resposta = "Informe a cidade onde deseja atendimento presencial."
            contexto["stage"] = "aguarda_cidade_presencial"
        else:
            resposta = "Opção inválida. Por favor, escolha 1 ou 2."

    elif stage == "aguarda_lgpd_online":
        if isinstance(mensagem, str) and mensagem.lower() in ["sim", "aceito"]:
            resposta = mensagem_falso_crime()
            contexto["stage"] = "aguarda_entendi_falso"
        else:
            resposta = "Não podemos prosseguir sem consentimento da LGPD."
            contexto["stage"] = "final"

    elif stage == "aguarda_entendi_falso":
        if isinstance(mensagem, str) and mensagem.lower() in ["sim", "entendi"]:
            resposta = "Por favor, informe seu nome completo."
            contexto["stage"] = "aguarda_nome_completo_inicial"
        else:
            resposta = "É preciso estar ciente do aviso para registrar a ocorrência."
            contexto["stage"] = "final"

    elif stage == "aguarda_nome_completo_inicial":
        contexto["nome_completo"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = f"{contexto['nome_completo']}, por favor me conte o que aconteceu detalhadamente."
        contexto["stage"] = "aguarda_descricao_inicial"

    elif stage == "aguarda_descricao_inicial":
        if isinstance(mensagem, str) and mensagem.strip():
            contexto["descricao_boletim"] = mensagem.strip()
            resposta = (
                "Certo, para prosseguir você prefere:\n"
                "1. Enviar anexos do seu documento de identidade (RG) e comprovante de residência\n"
                "2. Preencher os dados manualmente"
            )
            contexto["stage"] = "opcao_anexos_ou_formulario"
        else:
            resposta = "Por favor, descreva o que aconteceu para que eu possa ajudar."

    elif stage == "opcao_anexos_ou_formulario":
        escolha = mensagem.strip() if isinstance(mensagem, str) else ""
        if escolha == "1":
            resposta = (
                "Por favor, envie uma foto do seu documento de identidade (RG) e um comprovante de residência.\n"
                "Use o botão 📎 para anexar os arquivos.\n\n"
                "Quando terminar de enviar ambos, digite **'pronto'** para continuarmos."
            )
            contexto["stage"] = "aguarda_upload_documentos"
            contexto["documentos_recebidos"] = []
        elif escolha == "2":
            resposta = "Por favor, informe seu email para contato."
            contexto["stage"] = "aguarda_email_manual"
        else:
            resposta = "Opção inválida. Por favor, escolha 1 para anexar documentos ou 2 para preencher os dados."

    elif stage == "aguarda_upload_documentos":
        msg_normalizado = str(mensagem).strip().lower().replace("'", "").replace('"', "")
        if isinstance(mensagem, dict) and "filename" in mensagem:
            nome_arquivo = mensagem["filename"]
            contexto.setdefault("documentos_recebidos", []).append(nome_arquivo)
            resposta = f'Arquivo "{nome_arquivo}" enviado com sucesso! Por favor, envie o próximo ou digite "pronto" se já enviou todos.'
        elif msg_normalizado == "pronto":
            documentos = contexto.get("documentos_recebidos", [])
            documentos_enviados = contexto.get("documentos_enviados", [])
            
            # Verificar se tem RG/Identidade - aceitar vários tipos
            tem_rg = any(
                tipo in documentos_enviados 
                for tipo in ["rg", "identidade", "documento", "carteira"]
            ) or any(
                palavra in doc.lower() 
                for doc in documentos 
                for palavra in ["rg", "identidade", "id", "carteira", "documento"]
            )
            
            # Verificar se tem comprovante de residência
            tem_residencia = any(
                tipo in documentos_enviados 
                for tipo in ["comprovante", "residencia", "residência", "endereco"]
            ) or any(
                palavra in doc.lower() 
                for doc in documentos 
                for palavra in ["residencia", "residência", "comprovante", "endereco", "endereço"]
            )
            
            if tem_rg and tem_residencia:
                resposta = "Documentos recebidos com sucesso! Por favor, informe seu email para contato."
                contexto["stage"] = "aguarda_email"
            else:
                faltam = []
                if not tem_rg:
                    faltam.append("RG/Identidade")
                if not tem_residencia:
                    faltam.append("Comprovante de Residência")
                
                resposta = f"Ainda faltam os seguintes documentos: {', '.join(faltam)}. Por favor, envie-os e digite 'pronto'."
        else:
            resposta = "Por favor, envie os arquivos corretamente ou digite 'pronto' quando terminar."

    elif stage == "aguarda_email":
        contexto["email"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = "Por favor, confirme seu telefone para contato (ex: (51) 99999-9999)."
        contexto["stage"] = "aguarda_telefone"

    elif stage == "aguarda_telefone":
        contexto["telefone"] = mensagem.strip() if isinstance(mensagem, str) else ""
        protocolo = gerar_protocolo()
        resposta = (
            f"✅ Registro finalizado com sucesso!\n\n"
            f"Seu número de protocolo é: {protocolo}\n"
            f"Uma cópia do boletim será enviada para {contexto['email']}.\n"
            "Obrigado por utilizar os serviços do RSGOV. Se precisar de algo mais, é só chamar."
        )
        contexto["stage"] = "final"

    elif stage == "aguarda_email_manual":
        contexto["email"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = "Por favor, confirme seu telefone para contato (ex: (51) 99999-9999)."
        contexto["stage"] = "aguarda_telefone_manual"

    elif stage == "aguarda_telefone_manual":
        contexto["telefone"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = f"{contexto['nome_completo']}, me conte o que aconteceu detalhadamente."
        contexto["stage"] = "aguarda_descricao_boletim"

    elif stage == "aguarda_descricao_boletim":
        if isinstance(mensagem, str):
            contexto["descricao_boletim"] = mensagem.strip()
            resposta = "Informe o estado brasileiro onde sua Carteira de Identidade (RG) foi emitida (sigla)."
            contexto["stage"] = "aguarda_estado_rg"
        else:
            resposta = "Por favor, escreva um resumo do que aconteceu."

    elif stage == "aguarda_estado_rg":
        estado_rg = mensagem.strip().lower() if isinstance(mensagem, str) else ""
        if estado_rg in ["rs", "rio grande do sul"]:
            contexto["estado_rg"] = estado_rg.upper()
            resposta = "Digite o número da sua Carteira de Identidade (RG)."
            contexto["stage"] = "aguarda_numero_rg"
        else:
            resposta = "Para registro online no Rio Grande do Sul, é necessário que o RG tenha sido emitido no RS.\nSe seu RG é de outro estado, será preciso fazer o registro presencialmente."
            contexto["stage"] = "final"

    elif stage == "aguarda_numero_rg":
        contexto["numero_rg"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = "Por favor, informe seu CPF (apenas números)."
        contexto["stage"] = "aguarda_cpf"

    elif stage == "aguarda_cpf":
        cpf = mensagem.strip().replace(".", "").replace("-", "") if isinstance(mensagem, str) else ""
        if cpf.isdigit() and len(cpf) == 11:
            contexto["cpf"] = cpf
            resposta = "Informe sua data de nascimento no formato DD/MM/AAAA."
            contexto["stage"] = "aguarda_data_nascimento"
        else:
            resposta = "CPF inválido. Por favor, informe um CPF válido com 11 números."

    elif stage == "aguarda_data_nascimento":
        if isinstance(mensagem, str):
            try:
                data = datetime.strptime(mensagem.strip(), "%d/%m/%Y")
                contexto["data_nascimento"] = mensagem.strip()
                resposta = "Informe o nome completo da sua mãe, conforme consta no documento oficial."
                contexto["stage"] = "aguarda_nome_mae"
            except:
                resposta = "Formato inválido. Por favor, informe a data de nascimento no formato DD/MM/AAAA."
        else:
            resposta = "Formato inválido. Por favor, informe a data de nascimento no formato DD/MM/AAAA."

    elif stage == "aguarda_nome_mae":
        contexto["nome_mae"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = "Informe o nome completo do seu pai, conforme consta no documento oficial. Se não souber ou não quiser informar, digite 'não'."
        contexto["stage"] = "aguarda_nome_pai"

    elif stage == "aguarda_nome_pai":
        nome_pai = mensagem.strip().lower() if isinstance(mensagem, str) else ""
        if nome_pai == "não":
            nome_pai = ""
        contexto["nome_pai"] = nome_pai
        resposta = "Agora, por favor, informe seu CEP (apenas números)."
        contexto["stage"] = "aguarda_cep"

    elif stage == "aguarda_cep":
        cep = mensagem.strip() if isinstance(mensagem, str) else ""
        if cep.isdigit() and (7 <= len(cep) <= 9):
            contexto["cep"] = cep
            resposta = "Informe o nome da rua."
            contexto["stage"] = "aguarda_rua"
        else:
            resposta = "CEP inválido. Por favor, informe um CEP válido contendo apenas números."

    elif stage == "aguarda_rua":
        contexto["rua"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = "Informe o número da residência."
        contexto["stage"] = "aguarda_numero_residencia"

    elif stage == "aguarda_numero_residencia":
        contexto["numero_residencia"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = "Informe complemento, se houver. Caso não tenha, digite 'não'."
        contexto["stage"] = "aguarda_complemento"

    elif stage == "aguarda_complemento":
        complemento = mensagem.strip().lower() if isinstance(mensagem, str) else ""
        if complemento == "não":
            complemento = ""
        contexto["complemento"] = complemento
        resposta = "Informe o bairro."
        contexto["stage"] = "aguarda_bairro"

    elif stage == "aguarda_bairro":
        contexto["bairro"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = "Informe a cidade."
        contexto["stage"] = "aguarda_cidade"

    elif stage == "aguarda_cidade":
        contexto["cidade"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = "Informe o estado (sigla)."
        contexto["stage"] = "aguarda_estado"

    elif stage == "aguarda_estado":
        estado = mensagem.strip().upper() if isinstance(mensagem, str) else ""
        if len(estado) == 2 and estado.isalpha():
            contexto["estado"] = estado
            protocolo = gerar_protocolo()
            resposta = (
                f"✅ Registro finalizado com sucesso!\n\n"
                f"Seu número de protocolo é: {protocolo}\n"
                "Você pode usar este número para acompanhar a ocorrência no site da Delegacia Online.\n"
                "Obrigado por utilizar os serviços do RSGOV. Se precisar de algo mais, é só chamar."
            )
            contexto["stage"] = "final"
        else:
            resposta = "Estado inválido. Por favor, informe a sigla correta do estado, por exemplo: RS."

    elif stage == "aguarda_cidade_presencial":
        contexto["cidade"] = mensagem.strip() if isinstance(mensagem, str) else ""
        resposta = (
            f"Telefones e Contatos das Delegacias de Polícia na cidade de {contexto['cidade']}:\n"
            "- DHPP - DPPA/DIPAC - Volantes – EQ. A, B, C e D: 3288-2281 / Plantão da Volante 3288-2239\n"
            "- DPGV - Plantão 2131-5700, 2131-5760, 0800-6426400\n"
            "- DEIC - (051)3288-9866\n"
            "- DJO - 1ª DPPA: (051)3342-8547\n"
            "- DJO - 3ª DPPA: Secretaria/Plantão (051)3342-8513 (051)3325-6590\n"
            "Deseja o endereço ou telefone de alguma delegacia? Informe o nome ou 'não'."
        )
        contexto["stage"] = "aguarda_detalhe_delegacia"

    elif stage == "aguarda_detalhe_delegacia":
        escolha = mensagem.strip().lower() if isinstance(mensagem, str) else ""
        if escolha in ["delegacia central", "delegacia norte"]:
            resposta = (
                f"{escolha.title()}:\n"
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