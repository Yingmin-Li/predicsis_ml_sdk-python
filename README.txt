===========================
PredicSis ML SDK for Python
===========================

This SDK provides the bindings for PredicSis REST API in Python. 
Typical usage often looks like this::

    #!/usr/bin/env python

    from predicsis.api import PredicSisAPI
    api = PredicSisAPI(token="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", debug=1)
    dataset_id = api.create_dataset("file_path/train.dat", headers=True)
    result = api.create_dictionary(dataset_id, "Label")
    dictionary_id = result[0]
    target_var_id = result[1]
    model_id = api.create_model(dataset_id, target_var_id)
    scoreset_id = api.create_score(dictionary_id, model_id, "filepath/test.dat", "yes", headers=True)
    print(api.retrieve_scores(scoreset_id))
