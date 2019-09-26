test:
	pipenv run pomodoro test -v 2
build:
	docker-compose build
migrate:
	pipenv run pomodoro migrate
run: migrate
	pipenv run pomodoro runserver
shell: migrate
	pipenv run pomodoro shell
