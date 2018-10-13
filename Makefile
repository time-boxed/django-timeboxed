.PHONY: test run clean

test:
	pipenv run pomodoro test

run:
	pipenv run pomodoro migrate
	pipenv run pomodoro runserver

.env:
	pipenv install --dev
