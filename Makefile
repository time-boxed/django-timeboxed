.PHONY: test run clean

test:
	pipenv run pomodoro test
	pipenv run coverage html -d test-results
	pipenv run codecov

run:
	pipenv run pomodoro migrate
	pipenv run pomodoro runserver

.env:
	pipenv install --dev
