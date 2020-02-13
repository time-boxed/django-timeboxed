POMODORO_BIN := .venv/bin/pomodoro
PIP_BIN := .venv/bin/pip

.PHONY:	test build migrate run shell

test: ${POMODORO_BIN}
	${POMODORO_BIN} test -v 2

${POMODORO_BIN}:
	python3 -m venv .venv
	${PIP_BIN} install -r docker/requirements.txt
	${PIP_BIN} install -e .[dev,standalone]

build:
	docker-compose build
migrate: ${POMODORO_BIN}
	${POMODORO_BIN} migrate
run: migrate
	${POMODORO_BIN} runserver
shell: migrate
	${POMODORO_BIN} shell
