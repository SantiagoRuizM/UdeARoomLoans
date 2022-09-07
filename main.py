import os
import re
from argparse import ArgumentParser

logger = """import logging


class Format(logging.Formatter):
    grey = "\\x1b[38;21m"
    yellow = "\\x1b[33;21m"
    red = "\\x1b[31;21m"
    bold_red = "\\x1b[31;1m"
    reset = "\\x1b[0m"
    green = "\\x1b[32m"
    asctime = "%(asctime)s"
    name = "[%(name)s]"
    levelname = "[%(levelname)-4s]"
    message = "%(message)s"

    FORMATS = {
        logging.DEBUG: f"{asctime} {grey} {name} {levelname} {reset} {message}",
        logging.INFO: f"{asctime} {green} {name} {levelname} {reset} {message}",
        logging.WARNING: f"{asctime} {yellow} {name} {levelname} {message} {reset}",
        logging.ERROR: f"{asctime} {red} {name} {levelname} {message} {reset}",
        logging.CRITICAL: f"{asctime} {bold_red} {name} {levelname} {message} {reset}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def create_logger(logger_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(level=logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = Format()

    # file
    file = logging.FileHandler(f"{logger_name}.log")
    file.setLevel(level=logging.DEBUG)
    file.setFormatter(formatter)

    # console
    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(formatter)

    logger.addHandler(file)
    logger.addHandler(console)

    return logger
"""


config = """from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    ...


settings = Settings()
"""

main_file_content = """from argparse import ArgumentParser


def main():
    parser = ArgumentParser()

    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    main()

"""


def generate_directories(args):
    # generate the root directory of the source code
    os.makedirs(args.name, exist_ok=True)

    if args.tests:
        # the directory that will contains the tests files
        os.makedirs("tests", exist_ok=True)


def generate_files(args):
    # in order to consider the root directory as a python library directory
    open(os.path.join(args.name, "__init__.py"), "w").close()

    if args.config:
        with open(os.path.join(args.name, "config.py"), "w") as file:
            file.write(config)

    if args.logger:
        with open(os.path.join(args.name, "logger.py"), "w") as file:
            file.write(logger)


def configure_poetry_project(args):
    description = input("Write a project description: ") or "Default description"

    output_lines = []
    with open("pyproject.toml") as file:
        for line in file.readlines():
            if "name = " in line:
                line = re.sub(r"\"[\w\s-]+\"", f'"{args.name}"', line)
            if "description = " in line:
                line = re.sub(r"\"[\w\s-]+\"", f'"{description}"', line)

            if "[tool.poetry.dev-dependencies]" in line:
                if args.config:
                    output_lines[-1] = 'pydantic = "*"\n'
                    output_lines.append("\n")

            output_lines.append(line)

    with open("pyproject.toml", "w") as file:
        for line in output_lines:
            file.write(line)


def generate_docker_structure():
    os.makedirs("docker", exist_ok=True)
    with open("docker/Dockerfile", mode="a"):
        pass
    with open("docker/docker-compose-dev.yml", mode="a"):
        pass
    with open("docker/docker-compose-test.yml", mode="a"):
        pass
    with open("docker/docker-compose-prod.yml", mode="a"):
        pass


def execute(args):
    if args.all:
        args.tests = True
        args.config = True
        args.logger = True
        args.overwrite_main = True
        args.docker = True

    generate_directories(args)
    generate_files(args)
    configure_poetry_project(args)

    if args.docker:
        generate_docker_structure()

    if args.overwrite_main:
        with open("main.py", "w") as file:
            file.write(main_file_content)


def main():
    parser = ArgumentParser()

    parser.add_argument("-n", "--name", default="app", help="name of the project")
    parser.add_argument(
        "-t", "--tests", action="store_true", help="If the project will be tested"
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store_true",
        help="If the project need enviroment variables",
    )
    parser.add_argument(
        "-l",
        "--logger",
        action="store_true",
        help="If the project will have a logger system",
    )
    parser.add_argument(
        "-om",
        "--overwrite-main",
        action="store_true",
        help="If after execution the main file content will be erased",
    )
    parser.add_argument(
        "-d",
        "--docker",
        action="store_true",
        help="If the project will be deployed to a docker container",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="To add all generated files",
    )

    args = parser.parse_args()
    print(args)
    execute(args)


if __name__ == "__main__":
    main()
