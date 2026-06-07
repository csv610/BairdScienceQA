.PHONY: help venv install install-dev test format clean run-streamlit run-cli

help:
	@echo "BairdScienceQA - Available commands:"
	@echo "  make venv           Create virtual environment"
	@echo "  make install        Install dependencies"
	@echo "  make install-dev    Install dev dependencies"
	@echo "  make test           Run tests"
	@echo "  make format         Format code with black"
	@echo "  make lint           Run code linting"
	@echo "  make clean          Remove generated files"
	@echo "  make run-streamlit  Run Streamlit web app"
	@echo "  make run-cli        Run CLI tool"

venv:
	python3.12 -m venv bairdenv
	@echo "Virtual environment created! Activate with: source bairdenv/bin/activate"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt black pylint pytest-cov

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=. --cov-report=html

format:
	black baird/*.py app/*.py tests/

lint:
	pylint baird/*.py app/*.py

clean:
	rm -f *.mp3 *.pyc
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

run-streamlit:
	streamlit run app/bairdqa_sl.py

run-cli:
	python app/bairdqa_cli.py
