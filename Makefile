

VIRTUALENV_PATH=./venv
REQUIREMENTS_FILE_PATH=./requirements.txt
DEV_REQUIREMENTS_FILE_PATH=./requirements.dev.txt
TEST_REQUIREMENTS_FILE_PATH=./requirements.test.txt


SERVICE_NAME=thumbnails-service
FUNCTION_NAME=generate_thumbnails
IMAGES_BUCKET_NAME=images-bucket
IMAGES_DLQ_NAME=images-dlq


LOCALSTACK_ENDPOINT=http://localhost:4566


IMAGES_DLQ_URL=${LOCALSTACK_ENDPOINT}/000000000000/${IMAGES_DLQ_NAME}


AWS_CLI_LOCALSTACK_PROFILE=localstack
AWS_CLI_LOCALSTACK_PARAMETERS=--endpoint-url=${LOCALSTACK_ENDPOINT} --profile ${AWS_CLI_LOCALSTACK_PROFILE}


AWS_CLI=aws ${AWS_CLI_LOCALSTACK_PARAMETERS}


TEST_IMAGES_FOLDER=./test


install_git_hooks:
	pre-commit install


run_git_hooks:
	pre-commit run --all-files


create_virtualenv:
	@echo "Creating virtualenv..."
	python3 -m venv "${VIRTUALENV_PATH}"
	@echo "Done!"


install_requirements:
	@echo "Installing requirements..."
	${VIRTUALENV_PATH}/bin/pip install -r "${REQUIREMENTS_FILE_PATH}"
	@echo "Done!"


install_dev_requirements:
	@echo "Installing dev requirements..."
	${VIRTUALENV_PATH}/bin/pip install -r "${DEV_REQUIREMENTS_FILE_PATH}"
	@echo "Done!"


install_test_requirements:
	@echo "Installing test requirements..."
	${VIRTUALENV_PATH}/bin/pip install -r "${TEST_REQUIREMENTS_FILE_PATH}"
	@echo "Done!"


install_all_requirements: install_requirements install_test_requirements


run_unit_tests:
	@echo "Running unit tests..."
	@. ${VIRTUALENV_PATH}/bin/activate && python -m unittest discover -s functions -p '*_test.py'
	@echo "Done!"


run_integration_tests:
	@echo "Running integration tests..."
	@. ${VIRTUALENV_PATH}/bin/activate && python -m unittest discover -s integration_tests -p '*_test.py'
	@echo "Done!"


localstack_logs:
	localstack logs --follow


deploy_local:
	localstack stop || true
	localstack start -d
	sls deploy --stage local


deploy_function_local:
	sls deploy function --stage local --function ${FUNCTION_NAME}


tail_function_logs:
	${AWS_CLI} logs tail /aws/lambda/${SERVICE_NAME}-local-${FUNCTION_NAME} --follow


upload_test_images_to_s3:
	${AWS_CLI} s3 cp ${TEST_IMAGES_FOLDER} s3://${IMAGES_BUCKET_NAME}/images/ --recursive


messages_in_dlq:
	${AWS_CLI} sqs receive-message --queue-url ${IMAGES_DLQ_URL} --max-number-of-messages 10 --output json
