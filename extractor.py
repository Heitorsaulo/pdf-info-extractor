import openai
import os
import fitz
from pydantic import BaseModel
import json
from openpyxl import Workbook
import io
from API_info import ApiInfo

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


def create_excel_from_analysis(json_data: str) -> bytes:
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

    data = response_json.get("data", [])

    wb = Workbook()
    ws = wb.active
    ws.title = "Análise de Dados"

    if data:
        headers = list(data[0].keys())
        ws.append(headers)

        for row in data:
            ws.append(list(row.values()))

    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    return excel_file.read()


