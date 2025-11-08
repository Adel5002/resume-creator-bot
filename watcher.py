import argparse

from watchfiles import run_process

def start_bot() -> None:
    run_process(
        '.',  # следить за всем проектом
        target='python -m scripts.run_bot',  # что перезапускать
        watch_filter=lambda change, path: (
                'venv' not in path and
                '__pycache__' not in path and
                not path.endswith('.log')
        )
    )

def start_backend() -> None:
    run_process(
        '.',  # следить за всем проектом
        target='python -m backend.main',  # что перезапускать
        watch_filter=lambda change, path: (
                'venv' not in path and
                '__pycache__' not in path and
                not path.endswith('.log')
        )
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["start_bot", "start_backend"])
    args = parser.parse_args()

    if args.action == "start_bot":
        start_bot()
    elif args.action == "start_backend":
        start_backend()
