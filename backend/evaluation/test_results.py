from typing import Optional, Tuple

from common import submission_results_folder
from schema_classes.testing_schema import Results
from utils.p_types import error, new_error

file_id = "0"  # automatically set if needed
test_report_file = submission_results_folder.joinpath(f"test_results_{file_id}.json")


def save_test_results(results: Results) -> None:
    with open(test_report_file, "w") as f:
        f.write(results.to_json())


def load_test_results() -> Tuple[Optional[Results], error]:
    try:
        with open(test_report_file, "r") as f:
            return Results.from_json(f.read()), None
    except FileNotFoundError as e:
        return None, new_error(str(e))
    except Exception as e:
        return None, new_error(str(e))
