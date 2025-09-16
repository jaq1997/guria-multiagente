import requests
from datetime import datetime
from collections import defaultdict

API_KEY = "94905a03f2c483a2dc4c834340d70888"
BASE_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
BASE_FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

NIVEIS_RIOS = {
    "Porto Alegre": [("Guaíba", 3.3, 3.5)],
    "Novo Hamburgo": [("Rio dos Sinos", 2.8, 3.2)],
    "São Leopoldo": [("Rio dos Sinos", 2.8, 3.2)],
    "Eldorado do Sul": [("Jacuí", 3.5, 3.6)]
}

ABRIGOS = {
    "Porto Alegre": [
        "Escola São João, Rua ABC, 123 - Tel: (51)99999-1111",
        "Ginásio Navegantes, Av. Exemplo, 456 - Tel: (51)99999-2222"
    ],
    "Novo Hamburgo": [
        "Centro Comunitário NH, Av. Pátria, 10 - Tel: (51) 99999-3333"
    ]
}

def formatar_data(data_str):
    dt = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%d/%m/%Y")

def agente_clima(mensagem, contexto=None):
    if contexto is None:
        contexto = {}
    msg_lower = mensagem.lower().strip()
    etapa = contexto.get("etapa", "inicio")

    alerta = (
        "⛔ *Defesa Civil RS*: Atenção para risco de chuvas intensas e alagamentos na região metropolitana do estado. "
        "Em caso de emergência, ligue 199 ou consulte https://defesacivil.rs.gov.br/.\n"
    )

    if etapa == "inicio":
        resposta = (
            f"{alerta}\n"
            "Selecione uma das opções abaixo ou digite o número correspondente:\n"
            "1 - Previsão do tempo para os próximos 5 dias\n"
            "2 - Nível dos rios e cota de inundação\n"
            "3 - Abrigos disponíveis\n"
            "4 - Instruções de segurança/evacuação\n"
        )
        contexto["etapa"] = "menu"
        return resposta, contexto

    elif etapa == "menu":
        if msg_lower == "1":
            resposta = "Por favor, informe a cidade para consultar a previsão dos próximos 5 dias:"
            contexto["etapa"] = "previsao_cidade"
            return resposta, contexto
        elif msg_lower == "2":
            resposta = "De qual cidade você quer saber o nível dos rios e a cota de inundação?"
            contexto["etapa"] = "rios_cidade"
            return resposta, contexto
        elif msg_lower == "3":
            resposta = "Informe a cidade para listar abrigos disponíveis:"
            contexto["etapa"] = "abrigos_cidade"
            return resposta, contexto
        elif msg_lower == "4":
            resposta = (
                "🚨 Instruções para evacuação:\n"
                "- Prepare documentos e kit de emergência.\n"
                "- Vá para áreas altas ou abrigos indicados.\n"
                "- Escute as orientações da Defesa Civil local.\n"
                "Em caso de perigo, ligue 199.\n"
                "Digite outra opção ou 'sair' para encerrar."
            )
            contexto["etapa"] = "menu"
            return resposta, contexto
        elif msg_lower in ["sair", "cancelar", "voltar", "menu"]:
            contexto = {}
            resposta = "Encerrando o agente clima. Se precisar mais tarde, é só chamar!"
            return resposta, contexto
        else:
            resposta = "Opção inválida. Por favor, digite 1, 2, 3 ou 4."
            return resposta, contexto

    elif etapa == "previsao_cidade":
        cidade = mensagem.strip().title()
        contexto["cidade_previsao"] = cidade
        params = {
            "q": cidade,
            "appid": API_KEY,
            "units": "metric",
            "lang": "pt"
        }
        r = requests.get(BASE_FORECAST_URL, params=params)
        if r.status_code != 200:
            resposta = f"Não consegui encontrar dados para '{cidade}'. Por favor tente novamente."
            return resposta, contexto
        dados = r.json()
        lista = dados.get("list", [])
        # Agrupa por data
        temp_dias = defaultdict(list)
        condicoes = defaultdict(list)
        for item in lista:
            data = item['dt_txt'].split()[0]
            temp_min = item['main']['temp_min']
            temp_max = item['main']['temp_max']
            descricao = item['weather'][0]['description']
            temp_dias[data].append((temp_min, temp_max))
            condicoes[data].append(descricao)
        resposta = f"Previsão em {cidade} para os próximos 5 dias:\n"
        for data, temps in temp_dias.items():
            min_temp = min(t[0] for t in temps)
            max_temp = max(t[1] for t in temps)
            # clima mais frequente do dia
            from collections import Counter
            clima_freq = Counter(condicoes[data]).most_common(1)[0][0].capitalize()
            resposta += f"- {formatar_data(data + ' 00:00:00')}: {clima_freq}, min {min_temp}°C / max {max_temp}°C\n"
        resposta += "\nDigite outra opção do menu ou 'sair' para encerrar."
        contexto["etapa"] = "menu"
        return resposta, contexto

    elif etapa == "rios_cidade":
        cidade = mensagem.strip().title()
        contexto["cidade_rios"] = cidade
        rios = NIVEIS_RIOS.get(cidade)
        if rios:
            resposta = f"Nível dos rios em {cidade}:\n"
            for rio, nivel, cota in rios:
                resposta += f"- {rio}: {nivel}m (cota inundação: {cota}m)\n"
            resposta += "\nDigite outra opção do menu ou 'sair'."
        else:
            resposta = f"Não há dados de rios cadastrados para {cidade}.\nDigite outra opção ou 'sair'."
        contexto["etapa"] = "menu"
        return resposta, contexto

    elif etapa == "abrigos_cidade":
        cidade = mensagem.strip().title()
        contexto["cidade_abrigos"] = cidade
        abrigos = ABRIGOS.get(cidade)
        if abrigos:
            resposta = f"Abrigos disponíveis em {cidade}:\n- " + "\n- ".join(abrigos)
        else:
            resposta = f"Não há abrigos cadastrados para {cidade}."
        resposta += "\nDigite outra opção ou 'sair'."
        contexto["etapa"] = "menu"
        return resposta, contexto

    else:
        resposta = f"{alerta}\nNão entendi sua solicitação. Digite 1, 2, 3, 4 ou 'sair'."
        contexto["etapa"] = "menu"
        return resposta, contexto
