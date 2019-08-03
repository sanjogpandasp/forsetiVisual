from google.cloud import securitycenter as securitycenter
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from elasticsearch import Elasticsearch
import json
import datetime
import ConfigParser



# Setting up elastic client
global es 
es = Elasticsearch([{'host': '127.0.0.1', 'port': 9200}])
# Creating a client.
client = securitycenter.SecurityCenterClient()
# organization_id is the numeric ID of the organization. e.g.:
# organization_id = "111122222444"
# Replace your org id below
org_name = "organizations/111122222444"
# The "sources/-" suffix lists findings across all sources.  You
# also use a specific source_name instead.
# Replace your org id below
all_sources = "organizations/111122222444/sources/-"
# Setting the timestamp for the insertTime
now = datetime.datetime.now()
now_strftime = now.strftime("%Y-%m-%d")




def sccToElasticsearch():

    finding_result_iterator = client.list_findings(all_sources,filter_='state="ACTIVE"', page_size=200)
    for element in finding_result_iterator:
        jsonElement = MessageToDict(element.finding)

        # Flattening nested Json present in sourceProperties and deleting the parentKey. 
        # Deleting the resource_data key also as it is redudant.

        for elementInSourceProperties in jsonElement.get('sourceProperties').keys():
            jsonElement.update({elementInSourceProperties:jsonElement.get('sourceProperties').get(elementInSourceProperties)})
        del jsonElement['sourceProperties']
        del jsonElement['resource_data']

        # Normalizing violatio_data present in the jsonElement. 
        # violation_data might have a nested json or a string. Handling this using ast and
        # flattening violation_data key. Deleting the parentKey (violation_data) at the end. 
        violation = jsonElement.get('violation_data')
        violation = json.loads(violation)
        try:
            for item in violation.keys():
                jsonElement.update({'violation.'+item : violation.get(item)})

        except:
            jsonElement.update({'violation.location':violation})
        del jsonElement['violation_data']
        jsonElement.update({'insertTime':now_strftime})

        # Normalizing json to get the project_id based on the type of violation.
        # Reason : Different violation types give have project name in different key, hence kibana visualization breaks.
        # The dictionary of violation_type and the key for the project_id is maintained in config.property file.

        
        if jsonElement.get('category')=='BIGQUERY_VIOLATION':
            project_id = get_projectId('projectMapping',jsonElement.get('category'),jsonElement.copy()).split(':')[0]

        else:
            project_id = get_projectId('projectMapping',jsonElement.get('category'),jsonElement.copy())

        jsonElement.update({'project_id':project_id})
        
        #print jsonElement.get('category')
        print jsonElement
        print "\n\n\n\n\n\n"

        #Inserting the final document into elasticseach

        es.index(index='forseti',doc_type='forseti_finding', body=jsonElement)

def get_projectId(section,violation_type,jsonElement):
    config = ConfigParser.ConfigParser()
    config.read('config.property')
    x = config.get(section,violation_type)
    project_id=jsonElement.get(x)
    return project_id


if __name__ == "__main__":

    sccToElasticsearch()
