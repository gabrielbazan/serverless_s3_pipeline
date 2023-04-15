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

![Design](docs/diagram.png?raw=true "Design")

1. An image is stored to the images bucket
2. The image creation event is queued into an SQS queue
3. The lambda function tries to generate the thumbnails
4. 
    * **Success**: Thumbnails are saved to the thumbnails bucket
    * **Error**: 
        1. The message is retried as many times as configured in the queue
        2. If it continues to fail, the message is sent to a DLQ
        3. You can manually invoke another lambda function that dequeues from the DLQ and sends the messages back to the original queue to be retried


## Structure

The [serverless.yml](/serverless.yml) file contains the Serverless configuration to deploy the stack to either AWS or LocalStack.

The lambda functions are located in the [functions](/functions) package. Each AWS Lambda handler function is on a separate file. Common code is in the same package.

Unit tests are in the [functions/tests](/functions/tests) package.

Integration tests are in the [integration_tests](/integration_tests) package.

You can find useful commands in the [Makefile](/Makefile).

Python requirements:
  1. The *requirements.txt* file contains the essential Python dependencies required by the application logic to run.
  2. The *requirements.dev.txt* file contains the Python dependencies you need to have installed in your environment to contribute to the application logic.
  3. The *requirements.test.txt* file contains the Python dependencies required to run tests.


## Setup

### Install the Serverless Framework
```bash
npm install -g serverless
```

### Install LocalStack:
```bash
pip install localstack
```

### Install Serverless Framework Plugins

Go to the root directory of this repo and install the plugins:
```bash
cd serverless_s3_pipeline

npm i
```

### Install and Configure the AWS CLI

Follow [these instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) to install the AWS CLI.

To interact with LocalStack through the AWS CLI, you can create a profile with dummy region and access key.

Add this to your `~/.aws/config` file:
```
[profile localstack]
region = us-east-1
output = json
```

And this to your `~/.aws/credentials` file:
```
[localstack]
aws_access_key_id = dummyaccesskey
aws_secret_access_key = dummysecretaccesskey
```

## Deploy to LocalStack

Start LocalStack:
```bash
localstack start
```

Deploy to LocalStack:
```bash
serverless deploy --stage local
```

You should get something like the following. Notice the endpoint URL:
```
✔ Service deployed to stack thumbnails-service-local

functions:
  generate_thumbnails: thumbnails-service-local-generate_thumbnails
  retry_from_dlq: thumbnails-service-local-retry_from_dlq
```

You can alternatively start localstack as a daemon and deploy with a single command:
```bash
make deploy_local
```


## Makefile commands

### Install GIT Hooks

```bash
make install_git_hooks
```

### Run GIT Hooks

```bash
make run_git_hooks
```

### Create Python virtualenv

```bash
make create_virtualenv
```

### Install requirements into the virtualenv

```bash
make install_requirements
make install_dev_requirements
make install_test_requirements

# Or just
make install_all_requirements
```

### Run tests

```bash
make run_unit_tests
make run_integration_tests
```

### Deploy stack to LocalStack

Restarts LocalStack (if running) before deploying.

```bash
make deploy_local
```

### Deploy only the Lambda functions to LocalStack

```bash
make deploy_functions_local
```

### Show logs of the Lambda function that generates the thumbnails

```bash
make tail_generate_thumbnails_function_logs
```

### Show logs of the Lambda function that enqueues failed messages to retry

```bash
make tail_retry_from_sqs_function_logs
```

### Upload a few test images to the input bucket

```bash
make upload_test_images_to_s3
```

### Show up to 10 messages in the DLQ

```bash
make show_messages_in_dlq
```

### Invoke the Lambda function that enqueues failed messages to retry

```bash
make retry_from_dql
```
