from request import *

###
# Class for extracting MBeans metrics
###

class MBeansMetrics:
    def __init__(self, conf_data):
        self.url = conf_data['monitoring_urls']['mbeans']
        self.conf_data = conf_data
        
    def get_metrics(self, last_doc):
        self.mbeans_data = fetch_json_from_url(self.url)
        self.last_doc = last_doc
        
        mbeans_metrics = {}
        mbeans_metrics.update(self.get_docs_metrics())
        mbeans_metrics.update(self.get_queryhandler_metrics())
        mbeans_metrics.update(self.get_updatehandler_metrics())
        mbeans_metrics.update(self.get_cache_metrics())
        
        return mbeans_metrics
    
    def get_docs_metrics(self):
        docs_metrics = self.mbeans_data['solr-mbeans']['CORE']['searcher']['stats']
        
        return {
            "NUMDOCS" : docs_metrics['numDocs'],
            "MAXDOCS" : docs_metrics['maxDoc'],
            "DELETEDDOCS" : docs_metrics['deletedDocs']
        }
        
    ###
    # Get metrics for all the query handlers defined
    ###
    def get_queryhandler_metrics(self):
    
        # Get defined query handlers from config file
        query_handlers = self.conf_data['metrics']['query_handlers']
        
        # Extract and merge metrics for each of the query handlers
        queryhandler_metrics = {}
        for qhid in query_handlers:
            queryhandler_metrics.update(self.extract_queryhandler_metrics(qhid, query_handlers[qhid]))
        
        return queryhandler_metrics
    
    ###
    # Extract metrics for a query handler
    ###    
    def extract_queryhandler_metrics(self, qh_id, qh_name):
        
        qh_metrics = self.mbeans_data['solr-mbeans']['QUERYHANDLER'][qh_name]['stats']
        qh_id = qh_id.upper() 
        
        requests = qh_metrics['requests']
        timeouts = qh_metrics['timeouts']
        errors = qh_metrics['errors']
        total_time = qh_metrics['totalTime']
        
        es_keys = {
            'requests': "QUERYHANDLER_"+qh_id+"_REQUESTS",
            'timeouts': "QUERYHANDLER_"+qh_id+"_TIMEOUTS",
            'errors': "QUERYHANDLER_"+qh_id+"_ERRORS",
            'total_time': "QUERYHANDLER_"+qh_id+"_TOTALTIME",
            'throughput': "QUERYHANDLER_"+qh_id+"_THROUGHPUT",
            'timeout_rate': "QUERYHANDLER_"+qh_id+"_TIMEOUT_RATE",
            'error_rate': "QUERYHANDLER_"+qh_id+"_ERROR_RATE",
            'response_time': "QUERYHANDLER_"+qh_id+"_RESPONSE_TIME"
        }
        
        # Delta metrics
        throughput = 0
        response_time = 0
        timeout_rate = 0
        error_rate = 0
    
        if self.last_doc['hits']['total'] >= 1:
            doc = self.last_doc['hits']['hits'][0]['_source']
            if es_keys['requests'] in doc and requests >= doc[es_keys['requests']]:
                
                # Throughput - No. of requests processed in 1 minute
                throughput = requests - doc[es_keys['requests']]
                # No. of timeouts in 1 minute
                if es_keys['timeouts'] in doc:
                    timeout_rate = timeouts - doc[es_keys['timeouts']]
                # No. of errors in 1 minute
                if es_keys['errors'] in doc:
                    error_rate = errors - doc[es_keys['errors']]
                # Avg. response time for 1 minute window
                if es_keys['total_time'] in doc:
                    processing_time = total_time - doc[es_keys['total_time']]
                    if throughput > 0:
                        response_time = (total_time - doc[es_keys['total_time']])/throughput
                
        return {
            es_keys['requests'] : requests,
            es_keys['timeouts'] : timeouts,
            es_keys['errors'] : errors,
            es_keys['total_time'] : total_time,
            es_keys['throughput'] : throughput,
            es_keys['timeout_rate'] : timeout_rate,
            es_keys['error_rate'] : error_rate,
            es_keys['response_time'] : response_time
        }

    ###
    # Get metrics for all the update handlers defined
    ###
    def get_updatehandler_metrics(self):
    
        # Get defined update handlers from config file
        update_handlers = self.conf_data['metrics']['update_handlers']
        
        # Extract and merge metrics for each of the update handlers
        updatehandler_metrics = {}
        for uhid in update_handlers:
            updatehandler_metrics.update(self.extract_updatehandler_metrics(uhid, update_handlers[uhid]))
        
        return updatehandler_metrics
    
    ###
    # Extract metrics for an update handler
    ###    
    def extract_updatehandler_metrics(self, uh_id, uh_name):
        
        uh_metrics = self.mbeans_data['solr-mbeans']['UPDATEHANDLER'][uh_name]['stats']
        uh_id = uh_id.upper() 
        
        commits = uh_metrics['commits']
        autocommits = uh_metrics['autocommits']
        optimizes = uh_metrics['optimizes']
        cumulative_adds = uh_metrics['cumulative_adds']
        errors = uh_metrics['errors']
        tlog_size = uh_metrics['transaction_logs_total_size']
        tlog_number = uh_metrics['transaction_logs_total_number']
        
        es_keys = {
            'commits': "UPDATEHANDLER_"+uh_id+"_COMMITS",
            'autocommits': "UPDATEHANDLER_"+uh_id+"_AUTOCOMMITS",
            'optimizes': "UPDATEHANDLER_"+uh_id+"_OPTIMIZES",
            'cumulative_adds': "UPDATEHANDLER_"+uh_id+"_CUMULATIVEADDS",
            'errors': "UPDATEHANDLER_"+uh_id+"_ERRORS",
            'tlog_size': "UPDATEHANDLER_"+uh_id+"_TLOG_SIZE",
            'tlog_number': "UPDATEHANDLER_"+uh_id+"_TLOG_NUMBER",
            'commit_rate': "UPDATEHANDLER_"+uh_id+"_COMMIT_RATE",
            'autocommit_rate': "UPDATEHANDLER_"+uh_id+"_AUTOCOMMIT_RATE",
            'optimize_rate': "UPDATEHANDLER_"+uh_id+"_OPTIMIZE_RATE",
            'add_rate': "UPDATEHANDLER_"+uh_id+"_ADD_RATE",
            'error_rate': "UPDATEHANDLER_"+uh_id+"_ERROR_RATE"
        }
        
        # Delta metrics
        commit_rate = 0
        autocommit_rate = 0
        optimize_rate = 0
        add_rate = 0
        error_rate = 0
    
        if self.last_doc['hits']['total'] >= 1:
            doc = self.last_doc['hits']['hits'][0]['_source']
            if es_keys['commits'] in doc and commits >= doc[es_keys['commits']]:
                
                # No. of commits in 1 minute
                commit_rate = commits - doc[es_keys['commits']]
                # No. of auto commits in 1 minute
                if es_keys['autocommits'] in doc:
                    autocommit_rate = commits - doc[es_keys['autocommits']]
                # No. of optimizes in 1 minute
                if es_keys['optimizes'] in doc:
                    optimize_rate = optimizes - doc[es_keys['optimizes']]
                # No. of adds in 1 minute
                if es_keys['cumulative_adds'] in doc:
                    add_rate = cumulative_adds - doc[es_keys['cumulative_adds']]
                # No. of errors in 1 minute
                if es_keys['errors'] in doc:
                    error_rate = errors - doc[es_keys['errors']]
                
        return {
            es_keys['commits']: commits,
            es_keys['autocommits']: autocommits,
            es_keys['optimizes']: optimizes,
            es_keys['cumulative_adds']: cumulative_adds,
            es_keys['errors']: errors,
            es_keys['tlog_size']: tlog_size,
            es_keys['tlog_number']: tlog_number,
            es_keys['commit_rate']: commit_rate,
            es_keys['autocommit_rate']: autocommit_rate,
            es_keys['optimize_rate']: optimize_rate,
            es_keys['add_rate']: add_rate,
            es_keys['error_rate']: error_rate
        }
        
    ###
    # Get metrics for all the caches defined
    ###
    def get_cache_metrics(self):
    
        # Get defined caches from config file
        caches = self.conf_data['metrics']['caches']
        
        # Extract and merge metrics for each of the caches
        cache_metrics = {}
        for cid in caches:
            cache_metrics.update(self.extract_cache_metrics(cid, caches[cid]))
        
        return cache_metrics
    
    ###
    # Extract metrics for a cache
    ###    
    def extract_cache_metrics(self, c_id, c_name):
        
        c_metrics = self.mbeans_data['solr-mbeans']['CACHE'][c_name]['stats']
        c_id = c_id.upper() 
        
        return {
            "CACHE_"+c_id+"_LOOKUPS" : c_metrics['lookups'],
            "CACHE_"+c_id+"_HITS" : c_metrics['hits'],
            "CACHE_"+c_id+"_SIZE" : c_metrics['size'],
            "CACHE_"+c_id+"_EVICTIONS" : c_metrics['evictions'],
            "CACHE_"+c_id+"_INSERTS" : c_metrics['inserts']
        }
