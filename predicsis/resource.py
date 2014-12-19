from predicsis.api_client import APIClient
from collections import namedtuple
from predicsis import lvl_debug
import json
import datetime
from xml.dom import minidom

class APIResource(object): 
    @classmethod
    def res_name(cls):
        if cls.__name__ == 'APIResource':
            raise NotImplementedError('APIResource is an abstract class.')
        return cls.__name__.lower()
    
    @classmethod
    def res_url(cls):
        return cls.res_name() + 's'
    
    @classmethod
    def retrieve(cls, id):
        if (lvl_debug >= 1):
            print datetime.datetime + '\t' + 'Retrieving: ' + cls.res_name() + '..'
        json_data = APIClient.request('get', cls.res_url() + '/' + id)
        j = json_data[cls.res_name()]
        return json.loads(json.dumps(j), object_hook=lambda d: namedtuple(cls.res_name(), d.keys())(*d.values()))
    
    @classmethod
    def retrieve_all(cls):
        if (lvl_debug >= 1):
            print datetime.datetime + '\t' + 'Retrieving all: ' + cls.res_name() + '..'
        json_data = APIClient.request('get', cls.res_url())
        j = json_data[cls.res_url()]
        return json.loads(json.dumps(j), object_hook=lambda d: namedtuple(cls.res_name(), d.keys())(*d.values()))
    
    @classmethod
    def parse_data(cls, data):
        post_data = '{"' + cls.res_name() + '":{'
        for key, value in data.iteritems():
            if type(value).__name__ == "str" and not value=='true' and not value=='false':
                post_data += '"' + key +'":"' + value + '",'
            else:
                post_data += '"' + key +'":' + str(value).replace("'", "\"") + ','
        if post_data.endswith(','):
            post_data = post_data[0:-1]
        post_data += '}}'
        return post_data
    
class CreatableAPIResource(APIResource):
    @classmethod
    def create(cls, **data):
        if (lvl_debug >= 1):
            print datetime.datetime + '\t' + 'Creating: ' + cls.res_name() + '..'
        post_data = cls.parse_data(data)
        json_data = APIClient.request('post', cls.res_url(), post_data)
        j = json_data[cls.res_name()]
        if not hasattr(j, 'job_ids'):
            json_obj = json.loads(json.dumps(j), object_hook=lambda d: namedtuple(cls.res_name(), d.keys())(*d.values()))
            return json_obj
        else:
            jid = response[cls.res_name()]['job_ids'][0]
            status = 'pending'
            job = self.retrieve_job(jid)
            status = job['job']['status']
            while ((status != 'completed') and (status != 'failed')):
                job = cls.Job.retrieve(jid)
                status = job.status
                if status == 'failed':
                    raise Exception("Job failed! (job_id: " + job.id + ")")
            return cls.retrieve(j['id'])
    
class Project(CreatableAPIResource):
    pass

class Credentials(CreatableAPIResource):    
    @classmethod
    def res_url(cls):
        return 'sources/credentials'
    
class Source(CreatableAPIResource):
    pass
    
class DatasetAPI(CreatableAPIResource):
    @classmethod
    def res_name(cls):
        return 'dataset'
    
class Dataset(CreatableAPIResource):
    @classmethod
    def create(cls, **data):
        credentials = Credentials.retrieve('s3')
        payload = {
            'Content-Type':'multipart/form-data',
            'success_action_status':'201',
            'acl':'private',
            'policy':credentials.policy,
            'AWSAccessKeyId':credentials.aws_access_key_id,
            'signature':credentials.signature,
            'key':credentials.key
        }
        if (lvl_debug >= 1):
            print 'Uploading a file..'
        print data.get('file')
        files = {'file': open(data.get('file'),'rb')}
        response = APIClient.request_full(method='post', url=credentials.s3_endpoint, headers=[],post_data=payload, files=files)
        xmlResponse = minidom.parseString(response[0])
        keyList = xmlResponse.getElementsByTagName('Key')
        source = Source.create(name=data.get('file'), key=str(keyList[0].firstChild.data))
        sid = str(source.id)
        print sid
        return DatasetAPI.create(name=data.get('file'), header=str(data.get('header')).lower(), separator=data.get('separator').encode('string_escape'), source_ids=[sid])

class Job(APIResource):
    pass