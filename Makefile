APP_BIN := .venv/bin/pomodoro
PIP_BIN := .venv/bin/pip
PYTHON_BIN := .venv/bin/python

.PHONY:	test build migrate run shell clean

test: ${APP_BIN}
	${APP_BIN} test -v 2

${APP_BIN}:
	python3 -m venv .venv
	${PIP_BIN} install -r docker/requirements.txt
	${PIP_BIN} install -e .[dev,standalone]

build:	${PIP_BIN}
	${PYTHON_BIN} setup.py sdist
	twine check dist/*
migrate: ${APP_BIN}
	${APP_BIN} migrate
run: migrate
	${APP_BIN} runserver
shell: migrate
	${APP_BIN} shell
clean:
	rm -rf .venv
