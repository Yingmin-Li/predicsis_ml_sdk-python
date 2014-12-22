from predicsis.api_client import APIClient
from collections import namedtuple
import predicsis
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
        return '{%s}' % str(', '.join('"%s": %s' % (k, repr(v).replace("'","\"").replace("u\"","\"").replace("False","false").replace("True","true").replace("None","null")) for (k, v) in self.__dict__.iteritems()))
        
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
        if (predicsis.lvl_debug >= 1):
            predicsis.log('Retrieving: ' + cls.res_name() + '..')
        json_data = APIClient.request('get', cls.res_url() + '/' + id)
        j = json_data[cls.res_name()]
        return cls(j)
    
    @classmethod
    def retrieve_all(cls):
        if (predicsis.lvl_debug >= 1):
            predicsis.log('Retrieving all: ' + cls.res_name() + '..')
        json_data = APIClient.request('get', cls.res_url())
        j = json_data[cls.res_url().split('/')[-1]]
        return [cls(i) for i in j]
    
    @classmethod
    def parse_post_data(cls, data):
        post_data = '{"' + cls.res_name() + '":{'
        for key, value in data.iteritems():
            if (type(value).__name__ == "str" or type(value).__name__ == "unicode") and not value=='true' and not value=='false':
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
        if (predicsis.lvl_debug >= 1):
            predicsis.log('Creating: ' + cls.res_name() + '..')
        post_data = cls.parse_post_data(data)
        json_data = APIClient.request('post', cls.res_url(), post_data)
        j = json_data[cls.res_name()]
        try:
            jid = j['job_ids'][0]
            status = 'pending'
            job = Job.retrieve(jid)
            status = job.status
            while ((status != 'completed') and (status != 'failed')):
                job = Job.retrieve(jid)
                status = job.status
                if status == 'failed':
                    raise Exception("Job failed! (job_id: " + job.id + ")")
            return cls.retrieve(j['id'])
        except KeyError:
            return cls(j)

class UpdatableAPIResource(APIResource):
    to_update = {}
    
    def update(self, **data):
        for key, value in data.iteritems():
            self.to_update[key] = value
        
    def save(self):
        if (predicsis.lvl_debug >= 1):
            predicsis.log('Updating: ' + self.__class__.res_name() + '..')
        post_data = self.__class__.parse_post_data(self.to_update)
        json_data = APIClient.request('patch', self.__class__.res_url() + '/' + self.id, post_data)
        j = json_data[self.__class__.res_name()]
        try:
            jid = j['job_ids'][0]
            status = 'pending'
            job = Job.retrieve(jid)
            status = job.status
            while ((status != 'completed') and (status != 'failed')):
                job = Job.retrieve(jid)
                status = job.status
                if status == 'failed':
                    raise Exception("Job failed! (job_id: " + job.id + ")")
            return self.__class__.retrieve(j['id'])
        except KeyError:
            return self.__class__(j)
        
    def reset(self):
        self.to_update = {}

class DeletableAPIResource(APIResource):
    @classmethod
    def delete_all(cls):
        objs = cls.retrieve_all()
        for obj in objs:
            obj.delete()
            
    def delete(self):
        if (predicsis.lvl_debug >= 1):
            predicsis.log('Deleting: ' + self.__class__.res_name() + '..')
        APIClient.request('delete', self.__class__.res_url() + '/' + self.id)
        
class Job(DeletableAPIResource):
    pass
    
class Project(CreatableAPIResource, DeletableAPIResource):
    pass

class Credentials(CreatableAPIResource):    
    @classmethod
    def res_url(cls):
        return 'sources/credentials'
    
class Source(CreatableAPIResource, DeletableAPIResource):
    pass
    
class DatasetAPI(CreatableAPIResource, DeletableAPIResource):
    @classmethod
    def res_name(cls):
        return 'dataset'
    
class Dataset(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):
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
        if (predicsis.lvl_debug >= 1):
            predicsis.log('Uploading a file..')
        files = {'file': open(data.get('file'),'rb')}
        response = APIClient.request_full(method='post', url=credentials.s3_endpoint, headers=[],post_data=payload, files=files)
        xmlResponse = minidom.parseString(response[0])
        keyList = xmlResponse.getElementsByTagName('Key')
        if (predicsis.lvl_debug >= 1):
            predicsis.log('Creating: dataset..')
        source = Source.create(name=data.get('file'), key=str(keyList[0].firstChild.data))
        sid = str(source.id)
        dapi = DatasetAPI.create(name=name, header=str(header).lower(), separator=data.get('separator').encode('string_escape'), source_ids=[sid])
        return cls(json.loads(str(dapi)))
    
    def delete(self):
        if (predicsis.lvl_debug >= 1):
            predicsis.log('Deleting: ' + self.__class__.res_name() + '..')
        APIClient.request('delete', self.__class__.res_url() + '/' + self.id)
        if (predicsis.lvl_debug >= 1):
            predicsis.log('Deleting: source..')
        for id in self.source_ids:
            APIClient.request('delete', 'sources/' + id)
            
class Dictionary(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):        
    @classmethod
    def res_url(cls):
        return 'dictionaries'
    
class Variable(UpdatableAPIResource):
    dic_id = ''
    
    @classmethod
    def res_url(cls):
        return 'dictionaries/' + cls.dic_id + '/' + cls.res_name() + 's'
    
class ModalitiesSet(CreatableAPIResource, DeletableAPIResource):
    @classmethod
    def res_name(cls):
        return 'modalities_set'
    
            
class Target(CreatableAPIResource, DeletableAPIResource):         
    @classmethod
    def res_name(cls):
        return 'modalities_set'
    
    @classmethod
    def create(cls, target_var, dictionary_id, unused_vars=[]):
        if (predicsis.lvl_debug >= 1):
            predicsis.log('Retrieving: variables..')
        target_id = -1
        unused_ids = []
        dico = Dictionary.retrieve(dictionary_id)
        dataset_id = dico.dataset_id
        Variable.dic_id = dictionary_id
        variables = Variable.retrieve_all()
        i = 1
        for var in variables:
            if type(target_var).__name__ == "str":
                if var.name == target_var:
                    target_id = var.id
            elif type(target_var).__name__ == "int":
                if i == target_var:
                    target_id = var.id
            if var.name in unused_vars:
                var.update(use = False)
                var.save()
            elif i in unused_vars:
                var.update(use = False)
                var.save()
            i+=1
        if target_id == -1:
            raise Exception("Your target variable doesn't exist in the dataset.")
        if (predicsis.lvl_debug >= 1):
            print 'Creating: target..'
        modal = ModalitiesSet.create(variable_id = target_id, dataset_id = dataset_id)
        return cls(json.loads(str(modal)))
    
class PreparationRules(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):        
    @classmethod
    def res_name(cls):
        return 'preparation_rules_set'
    
class Classifier(CreatableAPIResource):  
    @classmethod
    def res_name(cls):
        return 'model'

class Model(CreatableAPIResource):
    @classmethod
    def create(cls, dataset_id, target_id):
        prs = PreparationRules.create(variable_id = target_id, dataset_id = dataset_id)
        clasif = Classifier.create(type='classifier',preparation_rules_set_id=prs.id)
        return cls(json.loads(str(clasif)))

class Scoreset(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):
    @classmethod
    def res_name(cls):
        return 'dataset'
    
    @classmethod
    def create(cls, dictionary_id, model_id, data, header=True,separator='\t'):
        response = Model.retrieve(model_id)
        prs_id = response.preparation_rules_set_id
        response = PreparationRules.retrieve(prs_id)
        var_id = response.variable_id
        Variable.dictionary_id = dictionary_id
        response = Variable.retrieve(var_id)
        modalities_set_id = response.modalities_set_ids[0]
        response = ModalitiesSet.retrieve(modalities_set_id)
        modalities = response.modalities
        if (predicsis.lvl_debug >= 1):
            print 'Preparing data..'
        dataset_id = -1
        file_name = ""
        try:
            open(data,'rb')
            file_name=data
            dataset_id = Dataset.create(file=data, header=header, separator=separator).id
        except IOError:
            file_name = self.storage + '/tmp.dat'
            f = open(file_name,'w')
            f.write(data)
            f.close()
            dataset_id = Dataset.create(file=file_name, header=header, separator=separator).id
        if dataset_id == -1:
            raise Exception("Error creating your test dataset")
        scoresets = []
        for modality in modalities:
            dataset = DatasetAPI.create(name='Scores', header=str(header).lower(), separator=separator.encode('string_escape'), classifier_id=model_id, dataset_id=dataset_id, modalities_set_id=modalities_set_id, main_modality=modality, data_file = { "filename": repr(file_name.split('/')[-1]).replace("'","")})
            scoreset = cls(json.loads(str(dataset)))
            scoresets.append(scoreset)
        return scoresets
    
    @classmethod
    def result(cls, scoresets):
        lines = []
        first = True
        for scoreset in scoresets:
            url = scoreset.data_file.url
            those_lines = APIClient.request_direct(url).text.split("\n")
            i = 0
            for l in those_lines:
                if first:
                    lines.append(l)
                else:
                    lines[i] += '\t' + l
                i+=1
            first = False
        return "\n".join(lines)
    
    @classmethod
    def delete_all(cls):
        pass

class ReportAPI(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):
    @classmethod
    def res_name(cls):
        return 'report'

class Report(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):
    @classmethod
    def create(cls, **data):
        type = data.get('type')
        if type == 'univariate_unsupervised':
            rep = ReportAPI.create(type=data.get('type'), dataset_id = data.get('dataset_id'), dictionary_id = data.get('dictionary_id'))
            return cls(json.loads(str(rep)))
        elif type == 'univariate_supervised':
            rep = ReportAPI.create(type=data.get('type'), dataset_id = data.get('dataset_id'), dictionary_id = data.get('dictionary_id'), variable_id = data.get('variable_id'))
            return cls(json.loads(str(rep)))
        elif type == 'classifier_evaluation':
            response = Model.retrieve(data['model_id'])
            prs_id = response.preparation_rules_set_id
            response = PreparationRules.retrieve(prs_id)
            var_id = response.variable_id
            Variable.dictionary_id = data.get('dictionary_id')
            response = Variable.retrieve(var_id)
            modalities_set_id = response.modalities_set_ids[0]
            rep = ReportAPI.create(type=data.get('type'), dataset_id = data.get('dataset_id'), modalities_set_id=modalities_set_id, classifier_id = data.get('model_id'), main_modality=data.get('main_modality'))
            return cls(json.loads(str(rep)))