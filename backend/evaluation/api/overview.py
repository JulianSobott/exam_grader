from data.api import overview_data
from schema_classes.overview_schema import OverviewRequestBase, OverviewGETRequest, OverviewGETResponse


class OverviewRequest(OverviewRequestBase):

    def handle_get(self, data: "OverviewGETRequest") -> "OverviewGETResponse":
        return overview_data()
