import streamlit as st
import pandas as pd
from functions import localizar_ppb, gerar_html, criar_quadro, criar_texto, html_AR

# Inicializa o estado global para armazenar dados
if "dados" not in st.session_state:
    st.session_state.dados = []

# Validação para garantir que o valor seja numérico
def validar_float(input_value):
    # Remove espaços extras e substitui vírgula por ponto
    input_value = input_value.replace(',', '.').strip()
    try:
        return float(input_value)
    except ValueError:
        return None

# Função principal
def main():
    st.title("Gerador de Avaliação de Risco (AR)")

    produto = st.text_input("Nome do Produto", key="produto")
    col1, col3 = st.columns([2, 2])

    with col1:
        ifa = st.text_input("IFA", key="ifa")
        fabricante = st.text_input("Fabricante", key="fabricante")
        planta_fabril = st.text_input("Planta Fabril", key="planta_fabril")
        difa = st.text_input("DIFA (DMF)", key="difa")
        
        # A validação de risco agora é sempre feita
        risco = st.number_input("Risco Global Calculado", min_value=0, key="risco")
        
    with col3:
        st.subheader("Predição de Ashworth")
        nitrosamina = st.text_input("Nitrosamina", key="nitrosamina")
        limite = st.text_input("Limite de Ingestão Diário (ng/dia)", key="limite")
        dose = st.text_input("Dose Máxima Diária (mg/dia)", key="dose")
        # Validação para garantir que o valor seja numérico
        limite = validar_float(limite)
        dose = validar_float(dose)
        ph = st.selectbox("Valor de pH", options=[3.15, 5, 7, 9], key="ph")
        pka = st.slider("pKa", min_value=9.5, max_value=14.0, step=0.1, value=9.5, key="pka")
        nitrito = st.selectbox("Níveis de Nitrito", options=["0.01 mg/L", "3 mg/L", "1 M"], key="nitrito")
        amina = st.selectbox("Quantidade de Amina", options=["1 mM", "1 M"], key="amina")
        temperatura = st.selectbox(
                "Temperatura (°C)", options=["25", "35", "45", "55", "25 (1 h)"], key="temperatura"
        )

        if st.button("Calcular Predição"):
            try:
                if limite is None or dose is None:
                    st.error("Por favor, insira um valor válido para os parâmetros.")
                valor_tabela = localizar_ppb(amina, nitrito, temperatura, ph)
                if valor_tabela == "Combinação inválida":
                    st.error("A combinação selecionada não existe no artigo.")
                # Salvar os valores de risco, nitrosamina e risco_nitrosamina no session_state
                risco_nitrosamina = "baixo" if (limite / dose > valor_tabela) else "alto"
                quadro = criar_quadro(ph, pka, nitrito, amina, temperatura, dose, limite)
                texto = criar_texto(ph, pka, nitrito, amina, temperatura, valor_tabela, nitrosamina, ifa, limite, dose)
                html_anexo = gerar_html(ifa, quadro, texto)
                st.download_button(
                    "Baixar Anexo Predição",
                    data=html_anexo,
                    file_name=f"Anexo_Predicao_{ifa}.html",
                    mime="text/html",
                )
                
            except Exception as e:
                st.error(f"Erro no cálculo: {e}")

    # Exibe a lista de IFAs adicionados com a opção de removê-los
    st.subheader("IFAs Adicionados")
    if "dados" not in st.session_state:
        st.session_state.dados = []

    if st.session_state.dados:
        # Cria um DataFrame para exibir os dados em forma de tabela
        dados_df = pd.DataFrame(st.session_state.dados)
        st.dataframe(dados_df)

        ifa_para_remover = st.selectbox(
            "Selecione um IFA para remover",
            options=[ifa['ifa'] for ifa in st.session_state.dados],
            key="select_ifa_remover"
        )

        if st.button("Remover IFA Selecionado"):
            if ifa_para_remover:
                index_to_remove = next((index for index, ifa in enumerate(st.session_state.dados) if ifa['ifa'] == ifa_para_remover), None)
                if index_to_remove is not None:
                    st.session_state.dados.pop(index_to_remove)
                    st.success(f"IFA '{ifa_para_remover}' removido com sucesso!")
                else:
                    st.error(f"Erro ao tentar remover o IFA '{ifa_para_remover}'.")

    # Botão para adicionar um novo IFA
    if st.button("Adicionar IFA"):
        if limite and dose:
            valor_tabela = localizar_ppb(amina, nitrito, temperatura, ph)
            risco_nitrosamina = "baixo" if (limite / dose > valor_tabela) else "alto"
        else:
            nitrosamina = None
            risco_nitrosamina = None
        st.session_state.dados.append(
            {
                    "ifa": ifa,
                    "fabricante": fabricante,
                    "planta_fabril": planta_fabril,
                    "difa": difa,
                    "risco": risco,
                    "nitrosamina": nitrosamina if nitrosamina else None,  # No caso de não haver nitrosamina
                    "risco_nitrosamina": risco_nitrosamina if risco_nitrosamina else None,  # No caso de não haver risco nitrosamina
            }
        )
        dados_df = pd.DataFrame(st.session_state.dados)
        st.dataframe(dados_df)
        st.success(f"IFA '{ifa}' adicionado com sucesso!")

    if st.button("Gerar Avaliação de Risco"):
        if not produto or not st.session_state.dados:
            st.error("Por favor, insira o nome do produto e adicione pelo menos um IFA.")
        else:
            html = html_AR(st.session_state.dados, produto)
            st.download_button(
                label="Baixar Avaliação de Risco",
                data=html,
                file_name=f"Avaliacao_Risco_{produto}.html",
                mime="text/html",
            )

if __name__ == "__main__":
    main()
