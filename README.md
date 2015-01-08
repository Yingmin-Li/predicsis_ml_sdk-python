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
    import predicsis
	
	# Initiate the API with your token
	predicsis.api_token='YOUR_SECRET_TOKEN'
	
	# Workflow from uploading a dataset to scores
	dataset = predicsis.Dataset.create(file='./Iris.dat',name='My Iris',header=True,separator='\t')
	dictionary = predicsis.Dictionary.create(name = 'My new dico', dataset_id = dataset.id)
	target = predicsis.Target.create(target_var = 'Class', dictionary_id = dictionary.id)
	model = predicsis.Model.create(dataset_id = dataset.id, variable_id = target.variable_id)
	scoresets = predicsis.Scoreset.create(dictionary_id = dictionary.id, model_id = model.id, data = './Iris.dat', header=True,separator='\t', name='Iris scored', file_name='iris_out.txt')
	print predicsis.Scoreset.result(scoresets)
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
