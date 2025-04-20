from pymongo import MongoClient
from typing import List, Dict


class MongoDBManager:
    def __init__(self, uri: str = "mongodb://localhost:27017/", db_name: str = "agrolink"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    # Inserções
    def inserir_produto(self, produto: Dict, collection_name="produtos"):
        return self.db[collection_name].insert_one(produto).inserted_id

    def inserir_varios_produtos(self, produtos: List[Dict], collection_name="produtos"):
        return self.db[collection_name].insert_many(produtos).inserted_ids

    # Consultas básicas
    def buscar_todos(self, collection_name="produtos"):
        return list(self.db[collection_name].find())

    def buscar_por_nome(self, nome_produto: str, collection_name="produtos"):
        return list(self.db[collection_name].find({"nome_produto": nome_produto}))

    def buscar_por_cultura(self, cultura: str, collection_name="produtos"):
        return list(self.db[collection_name].find({"indicacoes_uso.cultura": cultura}))

    def buscar_por_problema_regex(self, termo: str, collection_name="produtos"):
        return list(self.db[collection_name].find({
            "indicacoes_uso.problema": {"$regex": termo, "$options": "i"}
        }))

    def buscar_com_ordenacao(self, campo: str, crescente=True, collection_name="produtos"):
        direcao = 1 if crescente else -1
        return list(self.db[collection_name].find().sort(campo, direcao))

    # Atualizações
    def atualizar_nome_produto(self, antigo: str, novo: str, collection_name="produtos"):
        return self.db[collection_name].update_many(
            {"nome_produto": antigo},
            {"$set": {"nome_produto": novo}}
        )

    # Remoções
    def apagar_todos(self, collection_name="produtos"):
        return self.db[collection_name].delete_many({})

    # Consultas avançadas
    def buscar_links_por_problema(self, problema: str, collection_name="produtos"):
        return list(self.db[collection_name].find(
            {"indicacoes_uso.problema": problema},
            {"_id": 0, "link": 1}
        ))

    def produtos_com_multiplas_indicacoes(self, collection_name="produtos"):
        return list(self.db[collection_name].find(
            {"indicacoes_uso.1": {"$exists": True}}  # indica que há pelo menos 2
        ))

    def buscar_por_cultura_e_problema(self, cultura: str, problema: str, collection_name="produtos"):
        return list(self.db[collection_name].find({
            "indicacoes_uso": {
                "$elemMatch": {
                    "cultura": cultura,
                    "problema": problema
                }
            }
        }))

    def listar_nomes_unicos(self, collection_name="produtos"):
        return self.db[collection_name].distinct("nome_produto")

    def contar_por_problema(self, collection_name="produtos"):
        pipeline = [
            {"$unwind": "$indicacoes_uso"},
            {"$group": {"_id": "$indicacoes_uso.problema", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}}
        ]
        return list(self.db[collection_name].aggregate(pipeline))

    def buscar_resumo_por_problema_regex(self, termo: str, collection_name="produtos"):
        return list(self.db[collection_name].find(
            {"indicacoes_uso.problema": {"$regex": termo, "$options": "i"}},
            {"_id": 0, "nome_produto": 1, "link": 1}
        ))
