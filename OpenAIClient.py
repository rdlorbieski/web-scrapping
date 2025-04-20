from openai import OpenAI
import requests
import os
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

# Exemplo de modelo estruturado utilizando Pydantic
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

    def __str__(self):
        return f"Evento: {self.name}, Data: {self.date}, Participantes: {', '.join(self.participants)}"


class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        """
        Inicializa o cliente OpenAI.

        :param api_key: Chave da API do OpenAI
        :param model: Modelo a ser usado (padrão: "gpt-4-turbo")
        """
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send_pure_request(self, prompt: str, role_system: str, max_tokens: int = 1000):
        """
        Envia uma requisição para a API do OpenAI, podendo conter apenas texto ou texto + imagem.

        :param prompt: Texto enviado ao modelo.
        :param max_tokens: Número máximo de tokens para a resposta.
        :return: Resposta do modelo como string.
        """
        # Construção da mensagem do usuário
        message_content = [{"type": "text", "text": prompt}]

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": role_system},
                {"role": "user", "content": message_content}],
            "max_tokens": max_tokens
        }

        # Enviar requisição para a API
        response = requests.post(self.api_url, headers=self.headers, json=payload)

        # Processar a resposta
        if response.status_code == 200:
            response_data = response.json()
            if 'choices' in response_data and len(response_data['choices']) > 0:
                return response_data['choices'][0]['message']['content']
            else:
                return "O retorno da API não contém escolhas válidas."
        else:
            return f"Erro {response.status_code}: {response.json()}"


    def send_request(self, prompt: str, base64_image: str = None, max_tokens: int = 300):
        """
        Envia uma requisição para a API do OpenAI, podendo conter apenas texto ou texto + imagem.

        :param prompt: Texto enviado ao modelo.
        :param base64_image: String Base64 da imagem (opcional).
        :param max_tokens: Número máximo de tokens para a resposta.
        :return: Resposta do modelo como string.
        """
        # Construção da mensagem do usuário
        message_content = [{"type": "text", "text": prompt}]

        if base64_image:
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })

        # Payload para a API
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": message_content}],
            "max_tokens": max_tokens
        }

        # Enviar requisição para a API
        response = requests.post(self.api_url, headers=self.headers, json=payload)

        # Processar a resposta
        if response.status_code == 200:
            response_data = response.json()
            if 'choices' in response_data and len(response_data['choices']) > 0:
                return response_data['choices'][0]['message']['content']
            else:
                return "O retorno da API não contém escolhas válidas."
        else:
            return f"Erro {response.status_code}: {response.json()}"

    def send_request_structured_format(self, role_system, role_user, response_format, model):
        if model is None:
            model = self.model

        client = OpenAI(api_key=self.api_key)
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": role_system},
                {"role": "user", "content": role_user},
            ],
            response_format=response_format,
        )

        event = completion.choices[0].message.parsed
        return event



# api_key = os.getenv("GPT_KEY")
# openai_client = OpenAIClient(api_key=api_key, model="gpt-4o")
#
# # ce = openai_client.send_request_structured_format(
# #     role_system="Extract the event information.",
# #     role_user="Alice and Bob are going to a science fair on Friday.",
# #     response_format=CalendarEvent,
# #     model="gpt-4o-2024-08-06"
# #     )
# # print(ce)
#
# resultado = openai_client.send_request("Porque 2 elevado a 3 é 8?")
# print(resultado)

