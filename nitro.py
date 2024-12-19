import streamlit as st
import markdown
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.callbacks import get_openai_callback
from datetime import datetime
import os

# Acessar a chave da API a partir do Streamlit Secrets Manager
openai_api_key = st.secrets["openai"]["api_key"]
os.environ["OPENAI_API_KEY"] = openai_api_key

data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

def chat_rdc( prompt):
	llm = ChatOpenAI(temperature=0.5, model='gpt-4o-mini-2024-07-18')
	# Cria um template de prompt, no caso um sistema para indicar o tipo de resposta
	system_message = SystemMessage(content="""
		Você é um gerador de documentos para análise de nitrosaminas em medicamentos altamente eficiente.
		
        CONTEXTO:

        | Cenário | [Amina]  | Nível de Nitrito | Temp. (°C) | ppb produzido no pH da reação |
        |---------|----------|------------------|------------|---------------------------------------|
     pH |         |          |                  |            | 3,15         | 5          | 7          | 9          |
        | 1a      | 1 mM     | 0,01 mg/L        | 25         | 3,6.10⁻³     | 9,9.10⁻⁵   | 1.10⁻⁶     | 1.10-8     |
        | 1a      | 1 mM     | 0,01 mg/L        | 35         | 3,6.10⁻²     | 9,9.10⁻⁴   | 1.10⁻⁵     | 1.10-7     |
        | 1a      | 1 mM     | 0,01 mg/L        | 45         | 3,6.10⁻¹     | 9,9.10⁻³   | 1.10⁻⁴     | 1.10-6     |
        | 1a      | 1 mM     | 0,01 mg/L        | 55         | 3,6          | 9,9.10⁻²   | 1.10⁻³     | 1.10-5     |
        | 1b      | 1 mM     | 3 mg/L           | 25         | 1,5          | 5,3.10-2   | 5,3.10-4   | 5,3.10-6   |
        | 1b      | 1 mM     | 3 mg/L           | 35         | 14,7         | 5,3.10-1   | 5,3.10-3   | 5,3.10⁻⁵   |
        | 1b      | 1 mM     | 3 mg/L           | 45         | 147          | 5,3        | 5,3.10⁻²   | 5,3.10⁻⁴   |
        | 1b      | 1 mM     | 3 mg/L           | 55         | 1440         | 53         | 5,3.10⁻¹   | 5,3.10⁻³   |
        | 2a      | 1 M      | 0,01 mg/L        | 25         | 3,5          | 9,9.10⁻2   | 1,10-3     | 1,10-5     |
        | 2a      | 1 M      | 0,01 mg/L        | 35         | 32           | 9,9.10-1   | 1,10-2     | 1,10-4     |
        | 2a      | 1 M      | 0,01 mg/L        | 45         | 145          | 9,6        | 1,10⁻¹     | 1,10-3     |
        | 2a      | 1 M      | 0,01 mg/L        | 55         | 163          | 74         | 1          | 1,10⁻²     |
        | 2b      | 1 M      | 3 mg/L           | 25         | 1450         | 53         | 5,3.10⁻¹   | 5,3.10⁻³   |
        | 2b      | 1 M      | 3 mg/L           | 35         | 12300        | 521        | 5,3        | 5,3.10⁻²   |
        | 2b      | 1 M      | 3 mg/L           | 45         | 44200        | 4870       | 53         | 5,3.10-1    |
        | 2b      | 1 M      | 3 mg/L           | 55         | 48200        | 28900      | 530        | 5,3        |
        | 3       | 1 mM     | 1 M              | 25         | 740000       | 740000     | 54000      | 560        |
        | 3       | 1 mM     | 1 M              | 25* (1 h)  | 740000       | 210000     | 2500       | 25       |                              
		
        
        Você deve:
		- Utilizar a tabela acima para encontrar o meu 'ppb produzido no pH da reação' com base nos dados informados de pH, niveis de nitrito, quantidade de amina, temperatura.
        - Utilize o texto abaixo de modelo para resposta:

        No quadro 1 deste Anexo, foi inserido valores de pH (Valor do PH), pKa (Valor do pka), níveis de nitrito (Niveis de Nitrito), quantidade de amina (Quantidade de amina) e temperatura do processo (Temperatura), obtendo a quantidade de ('ppb produzido no pH da reação conforme quadro') formada, em ppb. Conforme predição teórica de Ashworth e colaboradores, a formação de (Nome da Nitrosamina) está abaixo de 10 % da especificação (VALOR CALCULADO AQUI). Desta forma, o risco para a formação de (Nome da Nitrosamina) no IFA (Nome do IFA) é baixo (ou alto se for acima de 10%).
        
		
        Sugestões:
		1. Gere acima do texto modelo o quadro 1 em markdown com os valores informados.
        2. Substitua os parenteses no modelo ajustando com os valores informados e remova os parenteses deixando melhor a visualização.
		3. Substitua 'VALOR CALCULADO AQUI' pelo resultado da divisão do limite da nitrosamina (ng/dia) pela dose máxima do medicamento (mg/dia) e obtendo valor em ppm.
        4. Substitua VALOR DA TABELA pelo valor encontrado no tabela'ppb produzido no pH da reação'
        4. Caso 'VALOR CALCULADO AQUI' não esteja abaixo de 10 por cento do valor de formação da minha nitrosamina com base na tabela, ajustar o percentual da especificação formado e alterar o risco para alto se acima de 10%.     
        5. Sempre colocar unidades de medida nos dados.                  
        """)
	# Prepara a mensagem do usuário (incluindo o contexto)
	user_message = HumanMessage(content=f"{prompt}")
	messages_to_send = [system_message, user_message]

	with get_openai_callback() as callback:
		response = llm(messages_to_send)
		tokens = callback.total_tokens
		custo = callback.total_cost
		# print(f"Tokens usados: {tokens}")
		# print(f"Custo estimado: ${custo:.6f}")		

	return response.content, tokens, custo

def render_markdown(text):
    # Converte o texto Markdown em HTML com a extensão 'tables'
    html = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists"]
    )

    return html
    
# Função para gerar o Arquivo
def gerar_html(conteudo, produto, data):   
    # Cria o HTML com a logo em base64
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório - {produto}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
            }}
            .container {{
                width: 90%;
                max-width: 800px;
                margin: 30px auto;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background-color: #0047AB;
                color: white;
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: space-between; /* Alinha logo à direita e título ao centro */
            }}
            .title {{
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                flex-grow: 1; /* Faz o título ocupar todo o espaço disponível e ficar centralizado */
            }}
            .content {{
                padding: 20px;
                line-height: 1.8;
                font-size: 16px;
            }}
            .footer {{
                background-color: #f1f1f1;
                text-align: center;
                padding: 10px 20px;
                font-size: 14px;
                color: #666;
            }}
            .highlight {{
                background-color: #ffefc2;
                padding: 5px 10px;
                border-radius: 5px;
                color: #b37400;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #0047AB;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="title">Relatório - Predição de Nitrosaminas - {produto}</div>
            </div>
            <div class="content">
                {conteudo}
            </div>
            <div class="footer">
                Relatório gerado em {data}.
            </div>
        </div>
    </body>
    </html>
    """
    return html

# Configuração da página
st.title("Predição de Nitrosaminas com LLM")
st.header("Insira os valores para gerar o relatório")

# Inputs do usuário
ifa = st.text_input("IFA")
nitrosamina = st.text_input("Nitrosamina")
limite = st.text_input("Limite de Ingestão Diário ng/dia")
dose = st.text_input("Dose Máxima Diária mg/dia")
ph = st.selectbox(
    "Selecione o valor de pH",
    options=[3.15, 5, 7, 9]
)
pka = st.slider("pKa", min_value=9.5, max_value=14.0, step=0.1, value=9.5)
nitrito = st.selectbox(
    "Níveis de Nitrito",
    options=["0,01 mg/L", "3 mg/L", "1 M"]
)
amina = st.selectbox(
    "Quantidade de Amina",
    options=["1 mM", "1 M"]
)
temperatura = st.selectbox(
    "Temperatura",
    options=['25°C', '35°C', '45°C', '55°C']
)

# Botão para gerar o relatório
if st.button("Gerar Relatório"):
    # Construir o prompt
    prompt = {f"""
        TENHO OS RESULTADOS A SEGUIR: 
        
        ifa = {ifa}
        nitrosamina = {nitrosamina}
        limite = {limite}
        dose = {dose}
        ph = {ph}
        pka = {pka}
        nitrito = {nitrito}
        amina = {amina}
        temperatura = {temperatura}
              
        """
    }
    # Chamar a função de IA
    resposta, _, _ = chat_rdc(prompt)
    resposta = render_markdown(resposta)
    # Mostrar a resposta no Streamlit
    st.subheader("Resposta da LLM:")
    st.markdown(resposta, unsafe_allow_html=True)

    # Gerar o Documento
    html_relatorio = gerar_html(resposta, ifa, data_hora)
    
    # Oferece o arquivo HTML para download
    st.download_button(
        label="Baixar Anexo",
        data=html_relatorio,
        file_name=f"Predicao_{ifa}.html",
        mime="text/html"
    )
