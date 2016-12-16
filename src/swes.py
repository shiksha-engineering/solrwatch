from elasticsearch import *
from request import *
import pprint

###
# Class for elasticsearch operations
###

class SWES:
    def __init__(self, conf_data):
        self.es = Elasticsearch([{'host': conf_data['elasticsearch']['host']}])
        self.index_name = conf_data['elasticsearch']['index']
        self.type_name = conf_data['elasticsearch']['type']
        self.conf_data = conf_data
        
    def insert(self, data):
        self.es.index(index=self.index_name, doc_type=self.type_name, body=data)

    def get_last_document(self):
        try:
            return self.es.search(index=self.index_name, body={"size": 1, "sort": {"DATETIME": {"order": "desc"}}})
        except:
            return self.get_blank_document()

    def get_blank_document(self):
        return {'hits': {'total': 0}}    
