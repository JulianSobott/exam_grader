import argparse
import logging
import sys
from dataclasses import dataclass, field
from typing import List, Callable

from common import submission_names, structured_submissions, raw_submissions
from tool_api import *
from utils.project_logging import get_logger

logger = get_logger(__name__)


def run():
    parsed = Command(
        name="grading",
        description="tool that helps grading java code",
        arguments=[
            Argument("-q", "--quiet", action="store_true"),
            Argument("-Q", "--Quiet", action="store_true"),
            Argument("-QQ", "--QUIET", action="store_true"),
        ],
        commands=[
            Command(
                name="copy",
                aliases=["1"],
                help="=description",
                description="prepare submissions for grading.",
                action=task(
                    lambda args: cli_extract(args),
                    "rename those files which have an incorrect name",
                    ["renamed", "test"]),
                arguments=[
                    Argument("zip_path"),
                    Argument("--test-names", action="store_true"),
                ]
            ),
            Command(
                name="renamed",
                aliases=["2"],
                description="Execute after all files are properly named",
                help="=description",
                action=task(lambda args: task_renamed_files(),
                            "test",
                            ["test"])
            ),
            Command(
                "test",
                aliases=["t", "3", "5"],
                description="run all tests",
                help="=description",
                arguments=[
                    Argument("--submissions")
                ],
                action=task(handle_run_tests_task,
                            "fix compilation errors or grade in the webinterface",
                            ["fixed", "web"])
            ),
            Command(
                name="fixed",
                aliases=["4"],
                description="Execute after fixing some submissions",
                help="=description",
                action=task(lambda args: git_fixed_code(),
                            "run tests again",
                            ["test"]),
            ),
            Command(
                name="web",
                aliases=["w"],
                description="start the web interface server",
                help="=description",
                action=lambda args: start_webserver(),
            ),
            Command(
                "git",
                arguments=[
                    Argument(
                        "task",
                        choices=["fixed_code", "renamed_files", "copied_files", "filled_files"]
                    )
                ]
            ),
            Command(
                name="env",
                description="show relevant environment variables",
                help="=description",
                action=lambda args: show_env_variables(),
            ),
            Command(
                name="fill",
                description="fill missing files",
                help="=description",
                action=task(lambda args: fill_missing_files(),
                            "run all tests",
                            ["test"])
            ),
            Command(
                name="exel",
                description="create an exel file with points and matrikel numbers",
                help="=description",
                action=lambda args: create_exel_table(),
            ),
            Command(
                name="reset_all",
                aliases=["0"],
                description="Removes all data from the db, deletes all structured submissions! ONLY BEFORE GRADING!",
                help="=description",
                action=task(lambda args: debug_reset_all())
            ),
            Command(
                name="dummy",
                description="Reset data, copy, fill, test. Use for testing only!",
                help="=descriptiion",
                action=task(lambda args: dummy_setup())
            )
        ],
    ).parse()

    if parsed.quiet:
        logger.setLevel(logging.INFO)
    if parsed.Quiet:
        logger.setLevel(logging.WARN)
    if parsed.QUIET:
        logger.setLevel(logging.ERROR)

    parsed.func(parsed)


def dummy_setup():
    debug_reset_all()
    task_copy_raw_to_structured()
    task_renamed_files()
    run_tests_for_all()
    start_webserver()


def cli_extract(args):
    if args.test_names:
        cli_output_file_failures()
    else:
        task_extract_zip(args.zip_path)
        cli_output_file_failures()


def handle_run_tests_task(args):
    if args.submissions:
        in_sub_list = list(map(str.strip, args.submissions.split(",")))
        out_sub_list = submission_names(in_sub_list)
        logger.info(f"running tests for: {out_sub_list}")
        run_tests_for_submissions(out_sub_list)
    else:
        run_tests_for_all()


def task(func: Callable, message: str = "", next_tasks: List[str] = ()):
    def arg_func(args):
        func(args)
        if message:
            print(f"\n\nNext: {message}")
        if next_tasks:
            print("")
            for t in next_tasks:
                print(f"\tpython cli.py {t}")
            print("")
    return arg_func


def show_env_variables():
    print(f"submission_folder={structured_submissions}")
    print(f"submission_raw_folder={raw_submissions}")


class Argument:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


@dataclass
class Command:
    name: str
    aliases: List[str] = field(default_factory=list)
    description: str = None
    help: str = None
    commands: List['Command'] = field(default_factory=list)
    action: Callable = lambda args: print(args)
    arguments: List[Argument] = field(default_factory=list)

    def parse(self):
        parser = self.get_argparser()
        parsed = parser.parse_args(sys.argv[1:])
        return parsed

    def get_argparser(self):
        def add_args(p: argparse.ArgumentParser, args):
            for arg in args:
                p.add_argument(*arg.args, **arg.kwargs)

        parser = argparse.ArgumentParser(prog=self.name, description=self.description)
        add_args(parser, self.arguments)

        sub_parsers = parser.add_subparsers(title="commands")
        for command in self.commands:
            if command.help == "=description":
                command.help = command.description
            sub_parser = sub_parsers.add_parser(
                command.name,
                description=command.description,
                help=command.help,
                aliases=command.aliases
            )
            add_args(sub_parser, command.arguments)
            sub_parser.set_defaults(func=command.action)
        return parser


if __name__ == '__main__':
    run()
