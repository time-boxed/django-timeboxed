.PHONY: test run clean

test: .env/bin/pomodoro
	.env/bin/pomodoro test

run: .env/bin/pomodoro
	.env/bin/pomodoro migrate
	.env/bin/pomodoro runserver

.env:
	python3 -m venv .env

.env/bin/pomodoro: .env
	.env/bin/pip install -e .[dev,standalone]

clean:
	rm -rf .env
