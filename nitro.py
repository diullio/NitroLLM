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

def logo_base64():
    logo = """
    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
    """
    return logo

def chat_rdc( prompt):
	llm = ChatOpenAI(temperature=0.5, model='gpt-4o-mini-2024-07-18')
	# Cria um template de prompt, no caso um sistema para indicar o tipo de resposta
	system_message = SystemMessage(content="""
		Você é um gerador de documentos para análise de nitrosaminas em medicamentos altamente eficiente.
		
        CONTEXTO:

        | Cenário | [Amina]  | Nível de Nitrito | Temp. (°C) | ppb produzido no pH da reação |
        |---------|----------|------------------|------------|---------------------------------------|
     pH |         |          |                  |            | 3,15         | 5          | 7          | 9          |
        | 1a      | 1 mM[^b] | 0,01 mg/L[^c]    | 25         | 3,6.10⁻³     | 9,9.10⁻⁵   | 1.10⁻⁶     | 1.10-8     |
        | 1a      | 1 mM[^b] | 0,01 mg/L[^c]    | 35         | 3,6.10⁻²     | 9,9.10⁻⁴   | 1.10⁻⁵     | 1.10-7     |
        | 1a      | 1 mM[^b] | 0,01 mg/L[^c]    | 45         | 3,6.10⁻¹     | 9,9.10⁻³   | 1.10⁻⁴     | 1.10-6     |
        | 1a      | 1 mM[^b] | 0,01 mg/L[^c]    | 55         | 3,6          | 9,9.10⁻²   | 1.10⁻³     | 1.10-5     |
        | 1b      | 1 mM[^b] | 3 mg/L[^d]       | 25         | 1,5          | 5,3.10-2   | 5,3.10-4   | 5,3.10-6   |
        | 1b      | 1 mM[^b] | 3 mg/L[^d]       | 35         | 14,7         | 5,3.10-1   | 5,3.10-3   | 5,3.10⁻⁵   |
        | 1b      | 1 mM[^b] | 3 mg/L[^d]       | 45         | 147          | 5,3        | 5,3.10⁻²   | 5,3.10⁻⁴   |
        | 1b      | 1 mM[^b] | 3 mg/L[^d]       | 55         | 1440         | 53         | 5,3.10⁻¹   | 5,3.10⁻³   |
        | 2a      | 1 M      | 0,01 mg/L[^c]    | 25         | 3,5          | 9,9.10⁻2   | 1,10-3     | 1,10-5     |
        | 2a      | 1 M      | 0,01 mg/L[^c]    | 35         | 32           | 9,9.10-1   | 1,10-2     | 1,10-4     |
        | 2a      | 1 M      | 0,01 mg/L[^c]    | 45         | 145          | 9,6        | 1,10⁻¹     | 1,10-3     |
        | 2a      | 1 M      | 0,01 mg/L[^c]    | 55         | 163          | 74         | 1          | 1,10⁻²     |
                                
        | 2b      | 1 M      | 3 mg/L[^d]       | 25         | 1450         | 53         | 5,3.10⁻¹   | 5,3.10⁻³   |
        | 2b      | 1 M      | 3 mg/L[^d]       | 35         | 12300        | 521        | 5,3        | 5,3.10⁻²   |
        | 2b      | 1 M      | 3 mg/L[^d]       | 45         | 44200        | 4870       | 53         | 5,3.10-1    |
        | 2b      | 1 M      | 3 mg/L[^d]       | 55         | 48200        | 28900      | 530        | 5,3        |
        | 3       | 1 mM[^b] | 1 M              | 25         | 740000       | 740000     | 54000      | 560        |
        | 3       | 1 mM[^b] | 1 M              | 25* (1 h)  | 740000       | 210000     | 2500       | 25                              
		
        
        Você deve:
		- Utilizar a tabela acima para calcular a minha formação de nitrosamina baseado nos dados informados de pH, niveis de nitrito, quantidade de amina, temperatura, encontrando a quantidade de ppb produzido no pH da reação.
        - Utilize o texto abaixo de modelo para resposta:

        No quadro 1 deste Anexo, foi inserido valores de pH (Valor do PH), pKa (Valor do pka), níveis de nitrito (Niveis de Nitrito), quantidade de amina (Quantidade de amina) e temperatura do processo (Temperatura), obtendo a quantidade de XX (Percentual e Nome da Nitrosamina) formada, em ppb. Conforme predição teórica de Ashworth e colaboradores, a formação de (Nome da Nitrosamina) está abaixo de 10 % da especificação (VALOR CALCULADO AQUI). Desta forma, o risco para a formação de (Nome da Nitrosamina) no IFA (Nome do IFA) é negligenciável (ou alto se for acima de 10%).
        
		
        Sugestões:
		1. Gere acima do texto modelo o quadro 1 em markdown com os valores informados.
        2. Substitua os parenteses no modelo ajustando com os valores informados e remova os parenteses deixando melhor a visualização.
		3. Substitua 'VALOR CALCULADO AQUI' pelo resultado da divisão do limite da nitrosamina (ng/dia) pela dose máxima do medicamento (mg/dia) e obtendo valor em ppm.
        4. Caso 'VALOR CALCULADO AQUI' não esteja abaixo de 10 por cento do valor de formação da minha nitrosamina com base na tabela, ajustar o percentual da especificação formado e alterar o risco para alto se acima de 10%.                       
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
    logo_base64 = logo_base64()
    
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
                <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="width: 50px; height: auto;">
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
limite = st.text_input("Limite de Ingestão Diário")
dose = st.text_input("Dose Máxima Diária")
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
