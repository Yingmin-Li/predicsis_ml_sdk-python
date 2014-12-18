from predicsis.api_client import APIClient
from collections import namedtuple
import json

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
        json_data = APIClient.request('get', cls.res_url() + '/' + id)
        j = json_data[cls.res_name()]
        return json.loads(json.dumps(j), object_hook=lambda d: namedtuple(cls.res_name(), d.keys())(*d.values()))
    
    @classmethod
    def retrieve_all(cls):
        json_data = APIClient.request('get', cls.res_url())
        j = json_data[cls.res_url()]
        return json.loads(json.dumps(j), object_hook=lambda d: namedtuple(cls.res_name(), d.keys())(*d.values()))
    
class CreatableAPIResource(APIResource):
    @classmethod
    def create(cls, **data):
        post_data = '{"' + cls.res_name() + '":{'
        for key, value in data.iteritems():
            post_data += '"' + key +'":"' + value + '",'
        if post_data.endswith(','):
            post_data = post_data[0:-1]
        post_data += '}}'
        json_data = APIClient.request('post', cls.res_url(), post_data)
        j = json_data[cls.res_name()]
        json_obj = json.loads(json.dumps(j), object_hook=lambda d: namedtuple(cls.res_name(), d.keys())(*d.values()))
        return json_obj
    
class Project(CreatableAPIResource):
    pass