from typing import Optional, Tuple

from common import test_report_folder, error
from schema_classes import Results

file_id = "0"   # automatically set if needed
test_report_file = test_report_folder.joinpath(f"test_results_{file_id}.json")


def save_test_results(results: Results) -> None:
    with open(test_report_file, "w") as f:
        f.write(results.to_json())


def load_test_results() -> Tuple[Optional[Results], error]:
    try:
        with open(test_report_file, "r") as f:
            return Results.from_json(f.read()), ""
    except FileNotFoundError as e:
        return None, error(str(e))
    except Exception as e:
        return None, error(str(e))
