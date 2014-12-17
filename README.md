# PredicSis ML SDK for Python.

The official PredicSis ML SDK for Python.

## Installation

To install the SDK, simply use [pip](https://pip.pypa.io/):

    $ pip install predicsis_ml_sdk

Or directly the developer version from GitHub:

    $ pip install git+https://github.com/PredicSis/predicsis_ml_sdk-python.git

## Getting started

You can start using our SDK assuming you already have a [user token](https://developer.predicsis.com/doc/v1/overview/oauth2/#get-authorization-from-a-user)

```python
    # Import the PredicSisAPI object
    from predicsis.api import PredicSisAPI
	
	# Initiate the API with your token
    api = PredicSisAPI(token="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
	
	# Create a dataset by providing your data file
    dataset_id = api.create_dataset("./iris.dat", header=True)
	
	# Create a dictionary by providing the dataset id
    dictionary_id = api.create_dictionary(dataset_id)
	
	# Create a dictionary by providing the dictionary id and the name of the target variable
    target_var_id = api.edit_dictionary(dictionary_id, "Class")
	
	# Create a model by providing the dataset id and the target variable id
    model_id = api.create_model(dataset_id, target_var_id)
	
	# Score your test dataset by providing the dictionary id, model id, and your test data file
    scoreset_ids = api.create_score(dictionary_id, model_id, "./iris.dat", header=True)
    print(api.retrieve_scores(scoreset_ids))
```

Resulting in case of the Iris dataset with:

```
	ProbClassIris-setosa	ProbClassIris-versicolor	ProbClassIris-virginica
    0.9977981	0.001100959	0.001100816
    0.9977958	0.001102631	0.001101537
    0.9977958	0.001102631	0.001101537
	...
```

## Getting Help

* [SDK wiki](https://github.com/PredicSis/predicsis_ml_sdk-python/wiki)
* [API doc](https://developer.predicsis.com/doc/v1/overview/)

## License

MIT. See the [LICENSE](https://github.com/PredicSis/predicsis_ml_sdk-python/blob/master/LICENSE) for more details.


## Contributing

1. Fork it
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create new Pull Request
