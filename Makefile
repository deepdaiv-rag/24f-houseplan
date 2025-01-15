.PHONY: install-precommit

install-precommit:
	pip install pre-commit

install-hooks:
	pre-commit install

pre-commit:
	pre-commit run --all-files

create-config:
	echo "repos:" > .pre-commit-config.yaml
	echo "  - repo: https://github.com/pre-commit/pre-commit-hooks" >> .pre-commit-config.yaml
	echo "    rev: v3.4.0" >> .pre-commit-config.yaml
	echo "    hooks:" >> .pre-commit-config.yaml
	echo "      - id: trailing-whitespace" >> .pre-commit-config.yaml
	echo "      - id: end-of-file-fixer" >> .pre-commit-config.yaml
	echo "      - id: check-yaml" >> .pre-commit-config.yaml
	echo "  - repo: https://github.com/psf/black" >> .pre-commit-config.yaml
	echo "    rev: 23.1.0" >> .pre-commit-config.yaml
	echo "    hooks:" >> .pre-commit-config.yaml
	echo "      - id: black" >> .pre-commit-config.yaml

setup: install-precommit create-config install-hooks
