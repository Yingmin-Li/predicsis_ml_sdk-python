# PredicSis ML SDK for Python.

The official PredicSis ML SDK for Python.

## Installation

To install the SDK, simply:

    $ pip install predicsis_ml_sdk

In order to be sure that you're up to date, you can also:

    $ pip install https://github.com/PredicSis/predicsis_ml_sdk-python

## Getting started

You can start using our SDK assuming you already have a [user token](https://developer.predicsis.com/doc/v1/overview/oauth2/#get-authorization-from-a-user)

```python
    # Import the PredicSisAPI object
    from predicsis.api import PredicSisAPI
	
	# Initiate the API with your token
    api = PredicSisAPI(token="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
	
	# Create a dataset by providing your data file
    dataset_id = api.create_dataset("file_path/train.dat", headers=True)
	
	# Create a dictionary by providing the dataset id and the name of the target variable
    result = api.create_dictionary(dataset_id, "Label")
    dictionary_id = result[0]
    target_var_id = result[1]
	
	# Create a model by providing the dataset id and the target variable id
    model_id = api.create_model(dataset_id, target_var_id)
	
	# Score your test dataset by providing the dictionary id, model id, your test data file and the modality of the target variable
    scoreset_id = api.create_score(dictionary_id, model_id, "filepath/test.dat", "yes", headers=True)
    print(api.retrieve_scores(scoreset_id))
```

## Getting Help

* [SDK documentation](https://github.com/PredicSis/predicsis_ml_sdk-python/wiki)
* [API documentation](https://developer.predicsis.com/doc/v1/overview/)

## License

MIT. See the [LICENSE](https://github.com/PredicSis/predicsis_ml_sdk/blob/master/LICENSE) for more details.


## Contributing

1. Fork it
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create new Pull Request