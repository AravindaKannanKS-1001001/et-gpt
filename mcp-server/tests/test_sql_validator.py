"""run_select must accept catalog SELECTs only."""
import json
import os

import pytest

from et_mcp.services.catalog import query
from et_mcp.services.catalog.sql_validator import SQLValidator

REGISTRY = os.path.join(os.path.dirname(query.__file__), "data", "schema_registry.json")
TABLE = next(iter(json.load(open(REGISTRY, encoding="utf-8"))))
V = SQLValidator(REGISTRY, schema="ragav", hidden_columns={"list_price", "price_usd"})


@pytest.mark.parametrize("sql", [
    f"SELECT model_name FROM {TABLE} LIMIT 5",
    f"SELECT model_name FROM ragav.{TABLE}",
    f"SELECT model_name FROM {TABLE} UNION SELECT model_name FROM {TABLE}",
    f"WITH t AS (SELECT model_name FROM {TABLE}) SELECT model_name FROM t",
])
def test_catalog_selects_pass(sql):
    assert V.validate(sql).is_valid, V.validate(sql).reason


@pytest.mark.parametrize("sql", [
    f"DELETE FROM {TABLE}",
    "SELECT 1; SELECT 2",
    f"CREATE TABLE {TABLE} (x int)",
    f"GRANT SELECT ON {TABLE} TO public",
    f"COPY {TABLE} TO STDOUT",
    f"SELECT model_name INTO newtab FROM {TABLE}",
    "SELECT query_to_xml('select * from auth.users', true, true, '')",
    "SELECT set_config('search_path', 'public', false)",
    "SELECT lo_import('/etc/passwd')",
    "SELECT pg_sleep(30)",
    f"SELECT model_name FROM auth.{TABLE}",
    "SELECT usename FROM pg_user",
    f"SELECT list_price FROM {TABLE}",
])
def test_unsafe_or_ungrounded_sql_is_rejected(sql):
    assert not V.validate(sql).is_valid


def test_search_products_rejects_filter_without_column():
    assert "column" in query.search_products(table=TABLE, filters=[{"value": "x"}])["error"]
