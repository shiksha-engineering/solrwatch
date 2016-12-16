from request import *
import pprint

###
# Class for extracting Admin metrics
###

class AdminMetrics:
    def __init__(self, conf_data):
        self.url = conf_data['monitoring_urls']['admin']
        self.conf_data = conf_data
        
    def get_metrics(self):
        admin_metrics_data = fetch_json_from_url(self.url)
        
        return {
            "JVM_MEMORY_FREE" : admin_metrics_data['jvm']['memory']['raw']['free'],
            "JVM_MEMORY_TOTAL" : admin_metrics_data['jvm']['memory']['raw']['total'],
            "JVM_MEMORY_MAX" : admin_metrics_data['jvm']['memory']['raw']['max'],
            "JVM_MEMORY_USED" : admin_metrics_data['jvm']['memory']['raw']['used'],
            "JVM_MEMORY_PERCENTUSED" : admin_metrics_data['jvm']['memory']['raw']['used%'],
            "SYSTEM_MEMORY" : admin_metrics_data['system']['totalPhysicalMemorySize']
        }
