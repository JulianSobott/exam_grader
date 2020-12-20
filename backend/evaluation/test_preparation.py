import unittest
from pathlib import Path
from typing import List, Generator
from unittest import mock

import preparation
from utils.p_types import _Error
from utils.project_logging import get_logger

logger = get_logger("TestPreparation")


class MockedPath:

    def __init__(self, path: str, content: List[Path], *, exists: bool = True):
        self.path = path
        self.content = content
        self._exists = exists

    def iterdir(self) -> Generator[Path, None, None]:
        for f in self.content:
            yield Path(self.path, f)

    def exists(self):
        return self._exists

    def mkdir(self, *args, **kwargs):
        return


class TestCopyFiles(unittest.TestCase):

    def setUp(self) -> None:
        preparation._copy_file_utf8 = mock.MagicMock()
        Path.mkdir = mock.MagicMock()
        Path.exists = lambda *args: False

    def test_valid(self):
        # prep
        students_name = "mustermann_max"
        mat_nr = "1234"
        file_name = "MyClass1.java"

        raw_folder = MockedPath("/raw", [
            Path(f"{students_name}{mat_nr}_question_11110_11111_{file_name}"),
        ])
        submission_folder = Path("/submissions")
        # execute
        err = preparation.copy_raw_to_structured(raw_folder, submission_folder)
        self.assertIsNone(err)

        # test
        preparation._copy_file_utf8.assert_called_once()
        Path.mkdir.assert_called_once()

    def test_invalid_file(self):
        # prep
        raw_folder = MockedPath("/raw", [
            Path(f"MyClass.java"),
        ])
        submission_folder = Path("/submissions")
        # execute
        err = preparation.copy_raw_to_structured(raw_folder, submission_folder)
        self.assertIsInstance(err, _Error)

        # test
        preparation._copy_file_utf8.assert_not_called()
        Path.mkdir.assert_not_called()
