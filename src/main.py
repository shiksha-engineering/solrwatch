from solrwatch import *
import schedule
import time
import pprint
import os
from datetime import datetime

def get_config():
    conf_file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/conf/app.conf'
    with open(conf_file) as json_data_file:
        conf_data = json.load(json_data_file)
        return conf_data

def job():
    start_time = datetime.utcnow()
    conf_data = get_config()
    
    # Run for each solr instance
    for name in conf_data:
        solrwatch = SolrWatch(conf_data[name], start_time)
        solrwatch.run()
    
if __name__ == "__main__":
    schedule.every(1).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
