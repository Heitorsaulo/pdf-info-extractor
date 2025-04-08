## Insight Extractor

Este projeto é uma aplicação baseada em FastAPI que extrai texto de arquivos PDF, processa o texto usando a API da OpenAI para extrair informações relevantes e gera um arquivo Excel com os dados extraídos. A aplicação inclui uma interface web para upload de arquivos PDF e visualização das informações extraídas.

### Integrantes da Equipe:
 - **Filipe Rodrigues Santana**
 - **Heitor Saulo Dantas Santos**
 - **Itor Carlos Souza Queiroz**

### Funcionalidades

- **Extração de Texto de PDF**: Extrai o texto de arquivos PDF enviados.
- **Extração de Informações**: Usa a API da OpenAI para analisar o texto e extrair pontos-chave e resumos.
- **Geração de Excel**: Cria um arquivo Excel com as informações extraídas.
- **Interface Web**: Oferece uma interface amigável para upload de PDFs e visualização dos resultados.

### Tecnologias Utilizadas

- **FastAPI**: Para construir a API do backend..
- **OpenAI API**: Para processar e extrair informações do texto.
- **Pandas**: Para criar e formatar arquivos Excel.

### Como Utilizar

1. Clone o repositório:
    ```sh
    git clone https://github.com/Heitorsaulo/pdf-info-extractor.git
    ```
2. Acesse a pasta do projetor
   ```
   cd pdf-info-extractor
   ```
3. Configure sua organização e projeto no arquivo `API_info.py`
   - Abra o arquivo API_info.py e defina os valores de self.organization e self.project com as informações da sua conta.

4. Crie um ambiente virtual e instale as dependências:
    ```sh
    python -m venv .venv
    source .venv/bin/activate # No Windows use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

5. Configure sua chave da API OpenAI:
    ```sh
    export MY_OPENAI_KEY='your-openai-api-key'  # No Windows use `set MY_OPENAI_KEY=sua-chave-openai`
    ```

6. Execute a aplicação:
    ```sh
    uvicorn main:app --reload
    ```

7. Execute o cliente:
    ```sh
    streamlit run .\pdf_extractor.py
    ```

8. Abra seu navegador e acesse `http://localhost:8501` para usar a interface web.
