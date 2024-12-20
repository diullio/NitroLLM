import streamlit as st
from datetime import datetime
import pandas as pd


def localizar_ppb(amina, nitrito, temperatura, pH):
    # Lê o arquivo CSV
    dados = pd.read_csv('tabela.csv')

    # Filtro para encontrar o valor correto
    resultado = dados[
        (dados["amina"] == amina) &
        (dados["nitrito"] == nitrito) &
        (dados["temperatura"] == temperatura) &
        (dados["pH"] == pH)
    ]

    # Verifica se o filtro encontrou resultados
    if resultado.empty:
        return "Combinação inválida"
    
    # Retorna o valor do ppb encontrado
    return resultado["ppb"].values[0]
    
# Função para gerar o Arquivo
def gerar_html(produto, quadro_1, texto_modelo):   
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
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .content {{
                padding: 20px;
                line-height: 1.8;
                font-size: 16px;
            }}
            .content p {{
                text-align: justify;
                text-indent: 1.5cm;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            th {{
                background-color: #d3d3d3; /* Cinza claro */
                color: #333;
                font-weight: bold;
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
            <div class="header">Relatório de Predição de Nitrosaminas</div>
            <div class="content">
                <p>{texto_modelo}</p>
                <h3>Quadro 1 - Valores Informados</h3>
                {quadro_1}
            </div>
        </div>
    </body>
    </html>
    """
    return html

# Configuração da página
st.title("Predição de Nitrosaminas")
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
    options=["0.01 mg/L", "3 mg/L", "1 M"]
)
amina = st.selectbox(
    "Quantidade de Amina",
    options=["1 mM", "1 M"]
)
temperatura = st.selectbox(
    "Temperatura °C",
    options=['25', '35', '45', '55', "25 (1 h)"]
)

# Função para criar o texto de saída
def criar_texto(valor_tabela, nitrosamina, ifa, limite, dose):
    # Calcula VALOR CALCULADO AQUI
    valor_calculado = (float(limite) / float(dose)) # Valor em ppm
    percentual = (valor_tabela / valor_calculado) * 100
    risco = "baixo" if percentual < 10 else "alto"

    # Define o texto baseado no percentual
    if percentual < 10:
        especificacao_texto = "abaixo de 10% da especificação"
    else:
        especificacao_texto = "acima de 10% da especificação"

    # Texto final
    texto = f"""
    No quadro 1 deste Anexo, foram inseridos valores de pH ({ph}), pKa ({pka}), níveis de nitrito ({nitrito}), quantidade de amina ({amina}) e temperatura do processo ({temperatura}°C), obtendo a quantidade de {valor_tabela} ppb formada. Conforme predição teórica de Ashworth e colaboradores, a formação de {nitrosamina} está {especificacao_texto} ({valor_calculado:.2e} ppm). Desta forma, o risco para a formação de {nitrosamina} no IFA {ifa} é {risco}.
    """
    return texto

# Quadro 1 em Markdown
def criar_quadro(ph, pka, nitrito, amina, temperatura, dose, limite):
    quadro = f"""
    <table>
        <thead>
            <tr>
                <th>pH</th>
                <th>pKa</th>
                <th>Níveis de Nitrito</th>
                <th>Quantidade de Amina</th>
                <th>Temperatura</th>
                <th>Dose Máxima (mg/dia)</th>
                <th>Limite de Nitrosamina (ng/dia)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{ph}</td>
                <td>{pka}</td>
                <td>{nitrito}</td>
                <td>{amina}</td>
                <td>{temperatura}°C</td>
                <td>{dose}</td>
                <td>{limite}</td>
            </tr>
        </tbody>
    </table>
    """
    return quadro

if st.button("Gerar Relatório"):
    # Busca o valor da tabela
    try:
        valor_tabela = localizar_ppb(amina, nitrito, temperatura, ph)
    except:
        st.error("Combinação inválida. Verifique os valores informados.")
        st.stop()

    st.write(f'Resultado: {valor_tabela} ppb')
    # Criar Quadro 1
    quadro_1 = criar_quadro(ph, pka, nitrito, amina, temperatura, dose, limite)

    # Gerar Texto de Saída
    texto_modelo = criar_texto(float(valor_tabela), nitrosamina, ifa, float(limite), float(dose))

    # Gerar o Documento HTML
    html_relatorio = gerar_html(ifa, quadro_1, texto_modelo)

    # Oferece o arquivo HTML para download
    st.download_button(
        label="Baixar Relatório",
        data=html_relatorio,
        file_name=f"Predicao_{ifa}.html",
        mime="text/html"
    )
