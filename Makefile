.PHONY: all test syntax verify clean help

help:
	@echo "Objectius disponibles:"
	@echo "  make test     Executa totes les suites de proves"
	@echo "  make syntax   Comprova la sintaxi de tots els moduls"
	@echo "  make verify   Comprova sintaxi i executa les suites"
	@echo "  make clean    Esborra els directoris __pycache__"

all: verify

test:
	python3 tests/run_all.py

syntax:
	python3 -m compileall -q shared projects governance tests

verify: syntax test
	@echo "Totes les comprovacions passades."

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
