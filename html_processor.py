import os
import requests
from pydantic import BaseModel
from typing import List
from bs4 import BeautifulSoup
import re

class IndicacaoUso(BaseModel):
    cultura: str
    problema: str

    def __str__(self):
        return f"Cultura: {self.cultura}, Problema: {self.problema}"

class Produto(BaseModel):
    nome_produto: str
    link: str
    indicacoes_uso: List[IndicacaoUso]

    def __str__(self):
        indicacoes_str = "\n".join(
            f"Cultura: {indicacao.cultura}, Problema: {indicacao.problema}"
            for indicacao in self.indicacoes_uso
        )
        return f"Produto: {self.nome_produto}\nLink: {self.link}\nIndicações de Uso:\n{indicacoes_str}"


class HTMLProcessor:
    def __init__(self, html, is_file):
        """
        Classe que recebe um arquivo HTML e realiza o processamento.
        :param html_file_path: Caminho para o arquivo HTML.
        """
        if is_file:
            if not os.path.exists(html):
                raise FileNotFoundError(f"O arquivo {html} não foi encontrado.")

            self.html_content = self._load_html(html)
        else:
            self.html_content = self.get_html_from_url(html)


    def get_html_from_url(self, url):
        """
        Faz uma requisição HTTP para o URL fornecido e retorna o HTML da página.
        :param url: URL da página da web.
        :return: Conteúdo HTML da página.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Verifica se a requisição teve sucesso (status 200).
            return response.text  # Retorna o conteúdo HTML como string.
        except requests.RequestException as e:
            print(f"Erro ao acessar o URL: {e}")
            return None

    def _load_html(self, html_file_path=None):
        """
        Carrega o conteúdo do arquivo HTML.
        """
        with open(self.html_file_path, "r", encoding="utf-8") as file:
            return file.read()

    def extrair_produto_agrolink(self, url, html_content: str) -> Produto:
        soup = BeautifulSoup(html_content, "html.parser")

        # Nome do produto
        nome_element = soup.find("h1", class_="section-title")
        nome_produto = nome_element.text.strip() if nome_element else "Desconhecido"

        # Indicações de uso
        indicacoes = []
        tabela = soup.find("table", {"id": "tb-crit-1"})
        if tabela:
            linhas = tabela.find_all("tr")
            for linha in linhas[1:]:
                colunas = linha.find_all("td")
                if colunas:
                    cultura = colunas[0].text.strip()
                    match = re.search(r'data-nomeproblema="([^"]+)"', str(linha))
                    problema = match.group(1) if match else "Problema não especificado"
                    indicacoes.append(IndicacaoUso(cultura=cultura, problema=problema))

        return Produto(nome_produto=nome_produto, link=url, indicacoes_uso=indicacoes)

    # def process_html(self):
    #     """
    #     Processa o conteúdo do HTML e retorna informações extraídas.
    #     Exemplo: Extrai todas as tags <a> e seus textos e links.
    #     """
    #     html_content = self.html_content
    #     #api_key = os.getenv("OPENAI_API_KEY")
    #     #openai_client = OpenAIClient(api_key=api_key, model="gpt-4o")
    #     role_system = """
    #     Você é um assistente que processa informações de produtos de sites específicos e retorna os dados formatados de maneira organizada.
    #     Certifique-se de basear sua resposta e estrutura nos modelos de dados Pydantic e devolver a saída como um objeto designado.
    #     Se o produto for solicitado, extraia apenas os campos necessários: nome_produto, link e indicacoes_uso (que contém cultura e problema).
    #     """
    #     role_user = """Por favor, processe o html: """+html_content+""" e retorne os dados formatados de maneira organizada."""
    #     produto = openai_client.send_request_structured_format(
    #         role_system=role_system,
    #         role_user=role_user,
    #         response_format=Produto,
    #         model="gpt-4o-2024-08-06"
    #     )
    #
    #     return produto


# Exemplo de uso
if __name__ == "__main__":
    link = "https://www.agrolink.com.br/agrolinkfito/produto/agdommon-nemaoff-bionexus-volga_11195.html"
    processor = HTMLProcessor(link, is_file=False)
    prod = processor.extrair_produto_agrolink(link, processor.html_content)
    #resultado = processor.process_html()
    print(prod)
