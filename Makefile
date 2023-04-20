

VIRTUALENV_PATH=./venv
REQUIREMENTS_FILE_PATH=./requirements.txt
DEV_REQUIREMENTS_FILE_PATH=./requirements.dev.txt
TEST_REQUIREMENTS_FILE_PATH=./requirements.test.txt


SERVICE_NAME=thumbnails-service

GENERATE_THUMBNAILS_FUNCTION_NAME=generate_thumbnails
GENERATE_THUMBNAILS_FUNCTION_FULL_NAME=${SERVICE_NAME}-local-${GENERATE_THUMBNAILS_FUNCTION_NAME}

RETRY_FROM_DLQ_FUNCTION_NAME=retry_from_dlq
RETRY_FROM_DLQ_FUNCTION_FULL_NAME=${SERVICE_NAME}-local-${RETRY_FROM_DLQ_FUNCTION_NAME}

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


install_all_requirements: install_requirements install_dev_requirements install_test_requirements


run_unit_tests:
	@echo "Running unit tests..."
	@. ${VIRTUALENV_PATH}/bin/activate && python -m unittest discover -s functions -p '*_test.py'
	@echo "Done!"


coverage:
	@echo "Generating code coverage report..."
	@. ${VIRTUALENV_PATH}/bin/activate && coverage run -m unittest discover -s functions -p '*_test.py' && coverage report -m && coverage html
	@echo "Done!"


run_integration_tests:
	@echo "Running integration tests..."
	@. ${VIRTUALENV_PATH}/bin/activate && python -m unittest discover -s integration_tests -p '*_test.py'
	@echo "Done!"


localstack_logs:
	localstack logs --follow


deploy_local:
	localstack stop || true
	DISABLE_EVENTS=1 localstack start -d
	sls deploy --stage local


deploy_functions_local: deploy_generate_thumbnails_function_local deploy_retry_from_dlq_function_local


deploy_generate_thumbnails_function_local:
	sls deploy function --stage local --function ${GENERATE_THUMBNAILS_FUNCTION_NAME}


deploy_retry_from_dlq_function_local:
	sls deploy function --stage local --function ${RETRY_FROM_DLQ_FUNCTION_NAME}


tail_generate_thumbnails_function_logs:
	${AWS_CLI} logs tail /aws/lambda/${GENERATE_THUMBNAILS_FUNCTION_FULL_NAME} --follow


tail_retry_from_sqs_function_logs:
	${AWS_CLI} logs tail /aws/lambda/${RETRY_FROM_DLQ_FUNCTION_FULL_NAME} --follow


upload_test_images_to_s3:
	${AWS_CLI} s3 cp ${TEST_IMAGES_FOLDER} s3://${IMAGES_BUCKET_NAME}/images/ --recursive


show_messages_in_dlq:
	${AWS_CLI} sqs receive-message --queue-url ${IMAGES_DLQ_URL} --max-number-of-messages 10 --output json


retry_from_dql:
	${AWS_CLI} lambda invoke --function-name ${RETRY_FROM_DLQ_FUNCTION_FULL_NAME} --invocation-type Event response.json	
	rm response.json
