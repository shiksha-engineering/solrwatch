from request import *
import pprint

###
# Class for extracting Luke metrics
###

class LukeMetrics:
    def __init__(self, conf_data):
        self.url = conf_data['monitoring_urls']['luke']
        self.conf_data = conf_data
        
    def get_metrics(self):
        luke_metrics_data = fetch_json_from_url(self.url)
        
        return {
            "SEGMENT_COUNT" : luke_metrics_data['index']['segmentCount']
        }
