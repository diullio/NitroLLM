import streamlit as st
from functions import localizar_ppb, gerar_html, criar_quadro, criar_texto, html_AR, montar_AR

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
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        ifa = st.text_input("IFA", key="ifa")
        fabricante = st.text_input("Fabricante", key="fabricante")
        planta_fabril = st.text_input("Planta Fabril", key="planta_fabril")
        difa = st.text_input("DIFA (DMF)", key="difa")
        risco = st.number_input("Risco Global Calculado", min_value=0, key="risco")
        predicao_necessaria = st.checkbox("Necessita Predição de Ashworth?", key="predicao")

    if predicao_necessaria:
        with col3:
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
                    if limite is None:
                        st.error("Por favor, insira um valor válido para o Limite de Ingestão Diário (ng/dia).")
                    if dose is None:
                        st.error("Por favor, insira um valor válido para a Dose Máxima Diária (mg/dia).")
                    valor_tabela = localizar_ppb(amina, nitrito, temperatura, ph)
                    if valor_tabela == "Combinação inválida":
                        st.error("A combinação selecionada não existe no artigo, tente novamente.")
                    quadro = criar_quadro(ph, pka, nitrito, amina, temperatura, dose, limite)
                    texto = criar_texto(ph, pka, nitrito, amina, temperatura, valor_tabela, nitrosamina, ifa, limite, dose)
                    html_anexo = gerar_html(ifa, quadro, texto)
                    st.download_button(
                        "Baixar Anexo Predição",
                        data=html_anexo,
                        file_name=f"Anexo_Predicao_{ifa}.html",
                        mime="text/html",
                    )
                    risco_nitrosamina = "baixo" if (limite / dose > valor_tabela) else "alto"
                except Exception as e:
                    st.error(f"Erro no cálculo: {e}")
    # Exibe a lista de IFAs adicionados com a opção de removê-los
    st.subheader("IFAs Adicionados")
    if st.session_state.dados:
        for index, ifa_data in enumerate(st.session_state.dados):
            col_remove, col_display = st.columns([1, 5])
            with col_display:
                st.write(f"{index + 1}. {ifa_data['ifa']} - {ifa_data['fabricante']}")
            with col_remove:
                if st.button(f"Remover {ifa_data['ifa']}", key=f"remove_{index}"):
                    st.session_state.dados.pop(index)
                    st.success(f"IFA '{ifa_data['ifa']}' removido com sucesso!")
                    break  # Saia do loop para evitar erro de modificação da lista durante iteração

    if st.button("Adicionar IFA"):
        st.session_state.dados.append(
            {
                "ifa": ifa,
                "fabricante": fabricante,
                "planta_fabril": planta_fabril,
                "difa": difa,
                "risco": risco,
                "nitrosamina": nitrosamina if predicao_necessaria else None,
                "risco_nitrosamina": risco_nitrosamina if predicao_necessaria else None,
            }
        )
        st.success(f"IFA '{ifa}' adicionado com sucesso!")

    if st.button("Gerar Avaliação de Risco"):
        if not produto or not st.session_state.dados:
            st.error("Por favor, insira o nome do produto e adicione pelo menos um IFA.")
        else:
            html = html_AR(st.session_state.dados, produto)
            docx_file = montar_AR(produto, html)
            with open(docx_file, "rb") as f:
                st.download_button(
                    label="Baixar Avaliação de Risco",
                    data=f,
                    file_name=docx_file,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )


if __name__ == "__main__":
    main()
