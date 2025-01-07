from jinja2 import Template
import pandas as pd
from docx import Document


#Ashworth
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

# Função para gerar o Arquivo da Predição
def gerar_html(produto, quadro_1, texto_modelo):   
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Anexo Predição - {produto}</title>
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

# Quadro 1 em HTML - Ashworth
def criar_quadro(ph, pka, nitrito, amina, temperatura, dose, limite):
    return f"""
    <table border="1">
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

# Função para criar o texto de saída
def criar_texto(ph, pka, nitrito, amina, temperatura, valor_tabela, nitrosamina, ifa, limite, dose):
    valor_calculado = float(limite) / float(dose)
    percentual = (valor_tabela / (valor_calculado * 1000)) * 100
    risco = "baixo" if percentual < 10 else "alto"
    especificacao_texto = (
        "abaixo de 10% da especificação" if percentual < 10 else "acima de 10% da especificação"
    )
    return f"""
    No quadro 1 deste Anexo, foram inseridos valores de pH ({ph}), pKa ({pka}), níveis de nitrito ({nitrito}), quantidade de amina ({amina}) e temperatura do processo ({temperatura}°C), obtendo a quantidade de {valor_tabela} ppb formada. Conforme predição teórica de Ashworth e colaboradores, a formação de {nitrosamina} está {especificacao_texto} ({valor_calculado:.2e} ppm). Desta forma, o risco para a formação de {nitrosamina} no IFA {ifa} é {risco}.
    """

#Funcao para gerar analise de risco
def html_AR(dados, produto):
    # Carrega o modelo HTML do arquivo `ar_model.html`
    with open("ar_model.html", "r", encoding="utf-8") as file:
        template = Template(file.read())

    # Renderiza o HTML com os dados fornecidos
    html = template.render(dados=dados, produto=produto)
    return html

