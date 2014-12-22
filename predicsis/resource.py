from predicsis.api_client import APIClient
from collections import namedtuple
from predicsis import lvl_debug
import json
import datetime
from xml.dom import minidom

class APIResource(dict):
    
    def __init__(self, obj):
        for k, v in obj.iteritems():
            if isinstance(v, dict):
                setattr(self, k, APIResource(v))
            else:
                setattr(self, k, v)
                
    def __getitem__(self, val):
        return self.__dict__[val]
    
    def __repr__(self):
        return '{%s}' % str(', '.join('"%s" : "%s"' % (k, v) for (k, v) in self.__dict__.iteritems()))
        
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
        return cls(j)
    
    @classmethod
    def retrieve_all(cls):
        if (lvl_debug >= 1):
            print datetime.datetime + '\t' + 'Retrieving all: ' + cls.res_name() + '..'
        json_data = APIClient.request('get', cls.res_url())
        j = json_data[cls.res_url()]
        return cls(j)
    
    @classmethod
    def parse_post_data(cls, data):
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
    
    @classmethod
    def construct_from(cls, data):
        print 'ERZERZ' + str(data)
        instance = cls()
        for k, v in data.iteritems():
            super(APIResource, instance).__setitem__(k, get_as_object(v))
        return cls()
    
class CreatableAPIResource(APIResource):
    @classmethod
    def create(cls, **data):
        if (lvl_debug >= 1):
            print datetime.datetime + '\t' + 'Creating: ' + cls.res_name() + '..'
        post_data = cls.parse_post_data(data)
        json_data = APIClient.request('post', cls.res_url(), post_data)
        j = json_data[cls.res_name()]
        if not hasattr(j, 'job_ids'):
            print "AAA " + str(j)
            return cls(j)
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

class UpdatableAPIResource(APIResource):
    to_update = {}
    
    def update(self, **data):
        for key, value in data.iteritems():
            self.to_update[key] = value
        
    def save(self):
        if (lvl_debug >= 1):
            print datetime.datetime + '\t' + 'Updating: ' + cls.res_name() + '..'
        post_data = self.__class__.parse_post_data(self.to_update)
        json_data = APIClient.request('patch', self.__class__.res_url() + '/' + self.id, post_data)
        j = json_data[self.__class__.res_name()]
        return self.__class__(j)
        
    def reset(self):
        self.to_update = {}
    
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
    
class Dataset(CreatableAPIResource, UpdatableAPIResource):
    @classmethod
    def create(cls, name="My dataset", header=True, **data):
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
        dapi = DatasetAPI.create(name=name, header=str(data.get('header')).lower(), separator=data.get('separator').encode('string_escape'), source_ids=[sid])
        print "XXX " + str(dapi)
        return cls(json.loads(str(dapi)))

class Job(APIResource):
    pass