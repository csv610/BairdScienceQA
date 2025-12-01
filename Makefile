.PHONY: help install install-dev test format clean run-streamlit run-cli

help:
	@echo "BairdScienceQA - Available commands:"
	@echo "  make install        Install dependencies"
	@echo "  make install-dev    Install dev dependencies"
	@echo "  make test           Run tests"
	@echo "  make format         Format code with black"
	@echo "  make lint           Run code linting"
	@echo "  make clean          Remove generated files"
	@echo "  make run-streamlit  Run Streamlit web app"
	@echo "  make run-cli        Run CLI tool"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt black pylint pytest-cov

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=. --cov-report=html

format:
	black src/*.py tests/

lint:
	pylint src/*.py

clean:
	rm -f *.mp3 *.pyc
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

run-streamlit:
	streamlit run src/bairdqa_sl.py

run-cli:
	python src/bairdqa_cli.py
