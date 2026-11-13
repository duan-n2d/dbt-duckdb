import pytest
from dbt.tests.util import run_dbt

upper_identifier_sql = """
{{ config(materialized='table') }}
select 1 as id
"""

upper_schema_sql = """
{{ config(materialized='table', schema='STAGING') }}
select 1 as id
"""

upper_view_sql = """
{{ config(materialized='view') }}
select 1 as id
"""


class TestUnquotedMixedCaseRelations:
    """
    With quoting disabled, dbt searches for the lowercased name while DuckDB keeps
    the original case in its catalog. Re-running must find the existing relation
    instead of raising an approximate match error (issue #905).
    """

    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"quoting": {"identifier": False, "schema": False}}

    @pytest.fixture(scope="class")
    def models(self):
        return {
            "MODEL.sql": upper_identifier_sql,
            "Staged_Model.sql": upper_schema_sql,
            "VIEW_MODEL.sql": upper_view_sql,
        }

    def test_second_run_succeeds(self, project):
        first = run_dbt(["run"])
        assert len(first) == 3

        second = run_dbt(["run"])
        assert len(second) == 3
        assert all(result.status == "success" for result in second)
