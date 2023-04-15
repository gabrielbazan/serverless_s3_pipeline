# Serverless S3 Pipeline

<p align="center">
    <a href="https://github.com/gabrielbazan/serverless_s3_pipeline/actions"><img alt="Test Workflow Status" src="https://github.com/gabrielbazan/serverless_s3_pipeline/workflows/Test/badge.svg"></a>
    <!-- <a href="https://coveralls.io/github/application-creators/create_app?branch=main"><img alt="Coverage Status" src="https://coveralls.io/repos/github/application-creators/create_app/badge.svg?branch=main"></a> -->
    <a href="https://www.python.org"><img alt="Python version" src="https://img.shields.io/badge/Python-3.8-3776AB.svg?style=flat&logo=python&logoColor=white"></a>
    <a href="https://github.com/pre-commit/pre-commit"><img alt="Pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white"></a>
    <a href="http://mypy-lang.org/"><img alt="Checked with mypy" src="http://www.mypy-lang.org/static/mypy_badge.svg"></a>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

Yet another AWS service to generate thumbnails. This one is based on AWS Lambda, S3, and SQS. 

It can be deployed to AWS or [LocalStack](https://github.com/localstack/localstack) using the [Serverless Framework](https://www.serverless.com/).

It also includes:
  * Unit tests.
  * Functional tests, which are executed against [LocalStack](https://github.com/localstack/localstack).
  * [Pre-commit](https://pre-commit.com/) hooks: [Black](https://github.com/psf/black), [ISort](https://pycqa.github.io/isort/), [Flake8](https://flake8.pycqa.org/en/latest/), and [MyPy](https://mypy-lang.org/).
  * A [Makefile](https://www.gnu.org/software/make/manual/make.html) with useful commands.


## Design

<p align="center">
  <img alt="Design" src="https://raw.githubusercontent.com/gabrielbazan/serverless_s3_pipeline/develop/docs/diagram.png">
</p>
