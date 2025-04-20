import streamlit as st
from pymongo import MongoClient
import openai
import os
import json

from OpenAIClient import OpenAIClient

# Configurações iniciais
st.set_page_config(page_title="Consultor MongoDB com GPT", layout="wide")

# Conexão Mongo
client = MongoClient("mongodb://localhost:27017/")
db = client["agrolink"]
collection = db["produtos"]

# Configuração da API do OpenAI
api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAIClient(api_key=api_key, model="gpt-4o")
role_system = """
Você tem acesso a um banco de dados MongoDB chamado `agrolink`, com a seguinte collection e estrutura:

---

1. Collection: produtos
   - Campos:
     - nome_produto (str): Nome comercial do produto agropecuário
     - link (str): URL com detalhes do produto no site
     - indicacoes_uso (list de objetos): cada item contém:
         - cultura (str): cultura agrícola em que o produto pode ser usado (ex: Cana-de-açúcar, Soja)
         - problema (str): praga, doença ou condição que o produto visa combater (ex: ferrugem, pulgão)

---

Use essas informações para responder perguntas sobre como consultar, filtrar, agrupar ou modificar dados.

Para cada pergunta do usuário:
1. **Responda diretamente com base no banco.**
2. Mostre a forma correta de fazer isso usando **MongoDB em Python**, usando `pymongo` e `collection = db["produtos"]`.

"""

st.title("🔍 Assistente GPT para Consultas MongoDB")

# Amostra de documento
sample = collection.find_one()
st.subheader("📄 Estrutura Exemplo do Banco")
st.json(sample)

prompt_input = st.text_input("Digite sua dúvida sobre o banco:", placeholder="Ex: Quero todos os produtos com problema ferrugem")
if st.button("Enviar para o GPT"):
    if prompt_input.strip() == "":
        st.warning("Digite um prompt antes de enviar.")
    else:
        resposta = openai_client.send_pure_request(prompt=prompt_input, role_system=role_system)
        st.text_area("Resposta do GPT:", value=resposta, height=800, key="resposta_gpt")
