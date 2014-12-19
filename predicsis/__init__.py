# coding: utf-8
#!/usr/bin/env python
#
# Copyright 2014-2015 PredicSis

'''
PredicSis REST API Python bindings.
API docs at https://developer.predicsis.com/doc/
Authors: Michal Szczerbak <michal.szczerbak@predicsis.com>
'''

__author__='mszczerbak'
__version__ ='0.1'

import logging
logger = logging.getLogger('predicsis')

api_token = None
api_url = 'https://api.predicsis.com/'
tmp_storage = '.'
lvl_debug = 0

from predicsis.resource import Project, Dataset#(Dataset, Dictionary, Modalities, Model, Scoreset, Report, Job)