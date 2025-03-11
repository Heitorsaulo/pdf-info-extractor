import streamlit as st
import requests
import base64
import json
import os

st.set_page_config(
    page_title="Insight Extractor",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Insight Extractor")

if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None
if "excel_bytes" not in st.session_state:
    st.session_state.excel_bytes = None
if "md_content" not in st.session_state:
    st.session_state.md_content = None
if "previous_file" not in st.session_state:
    st.session_state.previous_file = None

def clear_state():
    st.session_state.extracted_data = None
    st.session_state.excel_bytes = None
    st.session_state.md_content = None
    st.session_state.previous_file = None
    st.rerun()

def process_pdf(uploaded_file):
    """
    Args:
        uploaded_file (UploadedFile): File uploaded by the user.
    """
    with st.spinner("Processando arquivo PDF..."):
        try:
            files = {"file": uploaded_file}
            
            response = requests.post(
                "http://localhost:8000/extract_pdf", 
                files=files
            )
            response.raise_for_status()
            
            result = response.json()
            
            st.session_state.extracted_data = {
                "summary": result["summary"],
                "key_points": result["key_points"]
            }
            
            # Baixar o arquivo Excel e armazená-lo como bytes
            excel_response = requests.get(f"http://localhost:8000/download_excel?file_path={result['excel_file']}")
            excel_response.raise_for_status()
            st.session_state.excel_bytes = excel_response.content
            
            md_response = requests.get(
                f"http://localhost:8000/download_excel?file_path={result['markdown_file']}", 
                json={"summary": result["summary"], "key_points": result["key_points"]}
            )
            md_response.raise_for_status()
            st.session_state.md_content = md_response.content
            
            st.success("✅ Dados extraídos com sucesso!")
            
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Erro ao processar arquivo: {e}")

# Área de upload de arquivos com estilo personalizado
st.markdown("""
<style>
div.stFileUploader > div:first-child {
    padding: 30px;
    border: 2px dashed #ccc;
    border-radius: 8px;
    background-color: #f8f9fa;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload arquivo PDF", 
    type=["pdf"],
    help="Apenas arquivos PDF são permitidos"
)

# Se o arquivo anterior não for o mesmo, limpar o estado
if st.session_state.previous_file is not None and uploaded_file is None:
    clear_state()

if uploaded_file is not None:
    st.session_state.previous_file = uploaded_file
    
    if st.button("Extrair Informações"):
        process_pdf(uploaded_file)

# Exibir as informações extraídas
if st.session_state.extracted_data:
    st.subheader("ℹ️ Informações Extraídas")

    # Exibir pontos-chave
    st.markdown("### Key Points")
    for point in st.session_state.extracted_data["key_points"]:
        st.markdown(f"• {point}")
    
    # Exibir resumo
    st.markdown("### Summary")
    st.write(st.session_state.extracted_data["summary"])
    
    if st.session_state.excel_bytes:
        st.download_button(
            label="📥 Download Excel",
            data=st.session_state.excel_bytes,
            file_name="output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Clique para baixar o arquivo Excel com os dados extraídos"
        )
    
    if st.session_state.md_content:
        st.download_button(
            label="📥 Download Markdown",
            data=st.session_state.md_content,
            file_name="output.md",
            mime="text/markdown",
            help="Clique para baixar o arquivo Markdown com os dados extraídos"
        )
