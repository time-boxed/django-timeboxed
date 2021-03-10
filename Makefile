APP_BIN := .venv/bin/pomodoro
PIP_BIN := .venv/bin/pip
PYTHON_BIN := .venv/bin/python

.PHONY:	test build migrate run shell clean

test: ${APP_BIN}
	${APP_BIN} test

${APP_BIN}:
	python3 -m venv .venv
	${PIP_BIN} install -r docker/requirements.txt
	${PIP_BIN} install -e .[dev,standalone]


# Django and Python Commands

migrate: ${APP_BIN}
	${APP_BIN} migrate
run: migrate
	${APP_BIN} runserver
shell: migrate
	${APP_BIN} shell
clean:
	rm -rf .venv

# Docker and Release
.PHONY: build
build:
	docker-compose build 

.PHONY: release
release:	${PIP_BIN}
	${PYTHON_BIN} setup.py sdist
	twine check dist/*
