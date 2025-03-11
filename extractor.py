import openai
import os
import fitz
from pydantic import BaseModel
import json
from openpyxl import Workbook
import io
from API_info import ApiInfo
import pandas as pd
import re

api_info = ApiInfo()

org, project = api_info.get_info()

client = openai.OpenAI(
    organization=org,
    project=project,
    api_key=os.environ.get('MY_OPENAI_KEY')
)

# Configurar a chave da OpenAI (pode ser via variável de ambiente)
OPENAI_API_KEY = os.getenv("MY_OPENAI_KEY")


class ExtractedData(BaseModel):
    summary: str
    key_points: list[str]


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(page.get_text("text") for page in doc)
    return text.strip()

def add_summary_to_table(summary: str, table: pd.DataFrame) -> pd.DataFrame:
    summary_row = pd.DataFrame([{"Ponto Chave": "Resumo", "Valor": summary}])
    table_with_summary = pd.concat([summary_row, table], ignore_index=True)
    return table_with_summary

def modify_save_table(table: pd.DataFrame, output_path: str):
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        table.to_excel(writer, index=False, sheet_name='Análise de Dados')

        workbook = writer.book
        worksheet = writer.sheets['Análise de Dados']

        # Set the column width and format
        for column in table:
            column_width = max(table[column].astype(str).map(len).max(), len(column))
            col_idx = table.columns.get_loc(column)
            worksheet.set_column(col_idx, col_idx, column_width)

        # Add a header format
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })

        # Write the column headers with the defined format
        for col_num, value in enumerate(table.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Add a format for the summary row
        summary_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#FFEB9C',
            'border': 1
        })

        # Apply the summary format
        for col_num in range(len(table.columns)):
            worksheet.write(1, col_num, table.iloc[0, col_num], summary_format)

        # Apply the general format
        general_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })

        for row_num in range(1, len(table)):
            print(row_num)
            for col_num in range(len(table.columns)):
                worksheet.write(row_num+1, col_num, table.iloc[row_num, col_num], general_format)

def get_relevant_info_from_openai(text: str) -> str:
    prompt = f"""   
    Você é um assistente inteligente especializado em processar documentos com informações delicados, então é melhor pender para o excesso do que cortar informações importantes.
    Analise o seguinte texto e extraia as informações relevante.
    Não poupe detalhes, mas seja conciso, gostaria de ter todas as informações relevantes desse documento então é necessário procurar pelo maximo de informações relevantes possiveis.
    Evite repetição de informações, busque sempre informações novas.
    Retorne um resumo breve e uma lista de pontos-chave.
    Mantenha a resposta limpa, ou seja, somente retorne o conteúdo do JSON, nada mais.

    Texto do documento:
    {text}

    Responda no seguinte formato JSON:
    {{
        "summary": "<resumo do conteúdo>",
        "key_points": ["<ponto 1>", "<ponto 2>", "<ponto 3>", ...]
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=5000,
    )

    extracted_data = response.choices[0].message.content
    print(extracted_data)
    return extracted_data


def create_markdown_from_analysis(json_data: str) -> None:
    prompt = f"""
    Você é um assistente especializado na criação de documentos Markdown estruturados.
    Analise o seguinte JSON contendo um resumo e pontos-chave e converta-o em um documento Markdown bem organizado.
   
    Certifique-se de:
    - Usar corretamente a sintaxe Markdown para formatação
    - Manter a hierarquia das informações com cabeçalhos adequados (#, ##, ###)
    - Utilizar listas com marcadores (-) para os pontos-chave
    - Usar **negrito** para destacar títulos importantes
    - Preservar parágrafos com quebras de linha adequadas
    - Manter blocos de código, tabelas ou outras estruturas que possam estar presentes no conteúdo
   
    JSON de entrada:
    {json_data}
   
    Retorne APENAS o conteúdo Markdown finalizado, sem comentários adicionais ou explicações.
    Comece o documento com:
   
    # Resumo
    
    Seguido pelo conteúdo do resumo, e então:
    
    ## Pontos-Chave
    
    Seguido pelos pontos-chave formatados adequadamente.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=5000,
    )
    
    markdown_content = response.choices[0].message.content

    if not markdown_content:
        raise ValueError("Resposta vazia da API OpenAI")
   
    markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content.strip())

    outputh_path = 'static/output.md'
    with open(outputh_path, "w", encoding="utf-8") as file:
        file.write(markdown_content)

    
    return outputh_path


def create_excel_from_analysis(json_data: str) -> str:
    prompt = f"""
    Você é um assistente inteligente especializado em criar tabelas no Excel.
    Analise o seguinte JSON com informações chave e resumo, e crie um JSON que será tratado e transformado em uma tabela excel.
    Dessa forma, organize o JSON já em mente que ele será transformado em uma tabela.
    Mantenha a resposta limpa, ou seja, somente retorne o conteúdo do JSON, nada mais.

    JSON:
    {json_data}
    
    
    Responda no seguinte formato JSON:
        {{
            "data": [
                {{ "Ponto Chave": "<pontoChave1>", "Valor": "<valor1>" }},
                {{ "Ponto Chave": "<pontoChave2>", "Valor": "<valor2>" }},
                ...
            ]
        }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=5000,
    )

    response_content = response.choices[0].message.content

    print(response_content)


    if not response_content:
        raise ValueError("Empty response from OpenAI API")

    try:
        response_json = json.loads(response_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {e}")

    table = pd.DataFrame(response_json.get("data", []))
    relevant_info_json = json.loads(json_data)
    table_with_summary = add_summary_to_table(relevant_info_json['summary'], table)
    output_path = "static/output.xlsx"
    modify_save_table(table_with_summary, output_path)
    return output_path


