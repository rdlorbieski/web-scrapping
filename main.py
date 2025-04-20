from mongo_manager import MongoDBManager
from html_processor import HTMLProcessor

def carregar_links(arquivo: str) -> list:
    with open(arquivo, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]

def main():
    db = MongoDBManager()
    links = carregar_links("todos_links.txt")
    produtos = []

    for link in links:
        try:
            processor = HTMLProcessor(link, is_file=False)
            produto = processor.extrair_produto_agrolink(link, processor.html_content)
            produtos.append(produto.dict())
            print(f"✅ Sucesso: {produto.nome_produto}")
        except Exception as e:
            print(f"❌ Erro ao processar {link}: {e}")

    if produtos:
        db.inserir_varios_produtos(produtos)
        print(f"✔️ Inseridos {len(produtos)} produtos no MongoDB.")

if __name__ == "__main__":
    main()

