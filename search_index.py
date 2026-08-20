from elasticsearch import Elasticsearch
from typing import Dict, Any, List

class SearchIndex:
    def __init__(self, es_host: str = "http://localhost:9200"):
        self.es = Elasticsearch([es_host])
        self.index_name = "products"

    def index_product(self, product_id: str, document: Dict[str, Any]):
        self.es.index(index=self.index_name, id=product_id, document=document)

    def search_products(self, query_text: str = "", store_domain: str = None, category: str = None, min_price: float = None, max_price: float = None) -> List[Dict[str, Any]]:
        must_clause = []
        filter_clause = []

        if query_text:
            must_clause.append({"match": {"title": query_text}})
        else:
            must_clause.append({"match_all": {}})

        if store_domain:
            filter_clause.append({"term": {"domain.keyword": store_domain}})
        if category:
            filter_clause.append({"term": {"category.keyword": category}})
        
        if min_price is not None or max_price is not None:
            price_range = {}
            if min_price is not None:
                price_range["gte"] = min_price
            if max_price is not None:
                price_range["lte"] = max_price
            filter_clause.append({"range": {"price": price_range}})

        search_query = {
            "query": {
                "bool": {
                    "must": must_clause,
                    "filter": filter_clause
                }
            }
        }

        response = self.es.search(index=self.index_name, body=search_query)
        return [hit["_source"] for hit in response["hits"]["hits"]]-