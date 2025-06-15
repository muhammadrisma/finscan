.PHONY: install run

install:
	pip install -r requirements.txt

up-db:
	python -m src.app.db.init_db

down-db:
	python -m src.app.db.drop_db

reset-db:
	python -m src.app.db.reset_db

run:
	uvicorn app.app:app --reload --host 0.0.0.0 --port 8000

streamlit:
	streamlit run src/app/demo/demo.py