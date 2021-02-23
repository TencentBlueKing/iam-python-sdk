.PHONY: lint test init dist

lint:
	flake8 --config=.flake8 .

test:
	pytest --cov=iam -v tests/
	coverage report -m

init:
	pip install wheel
	pip install -r requirements.txt
	pip install -r requirements_test.txt

dist:
	python setup.py sdist bdist_wheel --universal
