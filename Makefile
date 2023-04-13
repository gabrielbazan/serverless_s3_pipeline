

VIRTUALENV_PATH=./venv
REQUIREMENTS_FILE_PATH=./requirements.txt
DEV_REQUIREMENTS_FILE_PATH=./requirements.dev.txt
TEST_REQUIREMENTS_FILE_PATH=./requirements.test.txt


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


deploy_local:
	localstack stop || true
	localstack start -d
	sls deploy --stage local


run_unit_tests:
	@echo "Running unit tests..."
	@. ${VIRTUALENV_PATH}/bin/activate && python -m unittest discover -s functions -p '*_test.py'
	@echo "Done!"


run_integration_tests:
	@echo "Running integration tests..."
	@. ${VIRTUALENV_PATH}/bin/activate && python -m unittest discover -s integration_tests -p '*_test.py'
	@echo "Done!"
