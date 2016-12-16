import json
import pprint
from datetime import datetime
import time
from mbeans_metrics import *
from admin_metrics import *
from luke_metrics import *
from swes import *

class SolrWatch:
    def __init__(self, conf_data, start_time):
        
        # Set config data and script start time
        self.conf_data = conf_data
        self.start_time = start_time
        
        # Create elasticsearch class instance
        self.swes = SWES(self.conf_data)

    def run(self):
        
        metrics = self.get_all_metrics()
        
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(metrics)
        
        # Insert into elasticsearch
        self.swes.insert(metrics)
        
    def get_all_metrics(self):
        
        # Fetch last indexed metrics document from elasticsearch
        # For delta calculations
        # e.g. throughput, response time etc.
        last_doc = self.swes.get_last_document()
        last_doc = self.last_doc_valid(last_doc)
        
        # Fetch metrics for MBeans, Admin and Luke 
        mbeans_metrics = MBeansMetrics(self.conf_data)
        admin_metrics = AdminMetrics(self.conf_data)
        luke_metrics = LukeMetrics(self.conf_data)

        # Merge all metrics
        solrwatch_metrics = {}
        solrwatch_metrics.update(mbeans_metrics.get_metrics(last_doc))
        solrwatch_metrics.update(admin_metrics.get_metrics())
        solrwatch_metrics.update(luke_metrics.get_metrics())

        # Add time
        solrwatch_metrics['DATETIME'] = self.start_time.strftime("%Y-%m-%dT%H:%M:00Z")
        
        return solrwatch_metrics
    
    # Check if last doc is valid for delta calculations
    # We collect metrics every minute
    # If last doc is more than 1 minute away from current time
    # Then it's not valid
    # Reason for this might be that the SolrWatch stopped
    # and run after some time    
    def last_doc_valid(self, last_doc):
        
        if last_doc['hits']['total'] == 0:
            return last_doc
        
        doc = last_doc['hits']['hits'][0]['_source']
        
        script_start_time = self.start_time.strftime("%Y-%m-%dT%H:%M:00Z")
        
        # Time difference in seconds between script start time and last doc time
        timediff = self.get_epoch(script_start_time) - self.get_epoch(doc['DATETIME'])
        
        # Difference should be a minute e.g. 60 seconds
        # Lets relax it to 70 seconds
        if timediff < 100:
            # Document is valid
            return last_doc
        else:
            # Return blank document
            # so that it will not be used for delta calculations
            return self.swes.get_blank_document()
    
    # Convert date string to epoch        
    # Date string format should be "%Y-%m-%dT%H:%M:00Z"
    def get_epoch(self, date_str):
        pattern = "%Y-%m-%dT%H:%M:00Z"
        return int(time.mktime(time.strptime(date_str, pattern)))
