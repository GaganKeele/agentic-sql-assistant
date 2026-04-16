from mcp_server.tools import date_context, sql_execution
from memory.database import init_database, get_schema

def test_date_context_has_required_keys():
    result = date_context("show sales for last month")
    assert "today" in result
    assert "last_month" in result
    assert "last_month_start" in result
    assert "last_month_end" in result

def test_date_context_last_month_format():
    result = date_context("test")
    # Verify dates are strings in correct format
    assert len(result["last_month_start"]) == 10  # YYYY-MM-DD
    assert result["last_month_start"] < result["last_month_end"]

def test_sql_execution_blocks_dangerous_queries():
    init_database()
    result = sql_execution("DROP TABLE sales")
    assert result["error"] is not None
    assert result["results"] == []

def test_sql_execution_select_works():
    init_database()
    result = sql_execution("SELECT COUNT(*) as count FROM products")
    assert result["error"] is None
    assert result["row_count"] == 1

def test_get_schema_returns_tables():
    init_database()
    schema = get_schema()
    assert "sales" in schema
    assert "products" in schema
    assert "customers" in schema