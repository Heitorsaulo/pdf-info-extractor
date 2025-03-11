from API_info import ApiInfo
import openai
import os

api_info = ApiInfo()

org, project = api_info.get_info()

client = openai.OpenAI(
    organization=org,
    project=project,
    api_key=os.environ.get('MY_OPENAI_KEY')
)

def generateResponseLLM(model: str, messages: object , max_tokens: int) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# Configurar a chave da OpenAI (pode ser via variável de ambiente)
OPENAI_API_KEY = os.getenv("MY_OPENAI_KEY")



