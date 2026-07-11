.PHONY: setup run test clean pipeline help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup:  ## Create venv and install dependencies
	python -m venv venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install pytest pytest-cov

pipeline:  ## Run full data pipeline (clean → enrich → load)
	python generate_dataset.py
	python clean_sales_data.py
	python enrich_sales_data.py
	python load_db.py

run:  ## Launch Streamlit dashboard
	streamlit run app.py

test:  ## Run pytest suite
	pytest tests/ -v

test-cov:  ## Run tests with coverage report
	pytest tests/ --cov=. --cov-report=term-missing

lint:  ## Run ruff linter
	ruff check .

format:  ## Format code with ruff
	ruff format .

clean:  ## Remove generated files
	rm -rf __pycache__ .pytest_cache .mypy_cache
	rm -f sales.db
	rm -f dataset/cleaned_sales_dataset.csv dataset/enriched_sales_dataset.csv

docker-build:  ## Build Docker image
	docker-compose build

docker-run:  ## Run with Docker Compose
	docker-compose up
