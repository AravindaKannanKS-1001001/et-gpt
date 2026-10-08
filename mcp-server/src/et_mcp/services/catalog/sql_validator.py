import json
# pyrefly: ignore [missing-import]
import sqlglot
# pyrefly: ignore [missing-import]
from sqlglot import exp
from pydantic import BaseModel

class ValidationResult(BaseModel):
    is_valid: bool
    read_only: bool
    tables_valid: bool
    columns_valid: bool
    reason: str

# Functions that can read server state, files or other tables through a string
# argument, change settings, or stall the connection. The table/column grounding
# below cannot see inside them, so they are rejected outright.
FORBIDDEN_FUNCTION_PREFIXES = ("pg_", "lo_", "dblink", "query_to_", "table_to_", "cursor_to_",
                               "schema_to_", "database_to_", "set_config", "current_setting",
                               "inet_", "txid_", "version")


class SQLValidator:
    def __init__(self, schema_registry_path: str = "schema_registry.json", schema: str | None = None,
                 hidden_columns: set[str] | None = None):
        with open(schema_registry_path, "r", encoding="utf-8") as f:
            self.schema_registry = json.load(f)

        # Create a fast lookup for table existence
        self.valid_tables = set(self.schema_registry.keys())
        self.schema = schema.lower() if schema else None
        self.hidden_columns = {c.lower() for c in (hidden_columns or set())}

    def validate(self, sql: str) -> ValidationResult:
        # 1. Syntax Check
        try:
            # Parse using Postgres dialect
            parsed = sqlglot.parse(sql, read="postgres")
            if not parsed or not parsed[0]:
                return self._fail("Syntax Check", "Could not parse SQL")
            # Reject stacked statements: only the FIRST is grounded/read-only checked
            # below, so a trailing statement (e.g. "SELECT 1; DROP TABLE t") would
            # otherwise ride through the escape hatch unvalidated.
            statements = [s for s in parsed if s is not None]
            if len(statements) > 1:
                return self._fail(
                    "Read-Only", "Multiple statements are not allowed (one SELECT only)")
            ast = statements[0]
        except (sqlglot.errors.ParseError, sqlglot.errors.TokenError) as e:
            return self._fail("Syntax Check", f"Invalid PostgreSQL syntax: {str(e)}")

        # 2. Read-Only Enforcement: the statement itself must be a query.
        if not isinstance(ast, (exp.Select, exp.Union, exp.Intersect, exp.Except, exp.Subquery)):
            return self._fail("Read-Only", f"Only SELECT queries are allowed (got {type(ast).__name__})")
        forbidden_nodes = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Drop,
            exp.Alter,
            exp.Command,
            exp.TruncateTable,
            exp.Create,
            exp.Into,
            exp.Merge,
            exp.Set,
            exp.Lock,
        )
        
        # ast.walk() yields the node directly
        for node in ast.walk():
            if isinstance(node, forbidden_nodes):
                return self._fail("Read-Only", f"Forbidden operation detected: {type(node).__name__}")

        for node in ast.find_all(exp.Func):
            fname = (node.name if isinstance(node, exp.Anonymous) else node.sql_name()).lower()
            if fname.startswith(FORBIDDEN_FUNCTION_PREFIXES):
                return self._fail("Read-Only", f"Function '{fname}' is not allowed")

        # 3. Table Grounding
        extracted_tables = set()
        for node in ast.find_all(exp.Table):
            table_name = node.name.lower()
            schema_name = (node.db or "").lower()
            if node.catalog or (schema_name and schema_name != self.schema):
                return self._fail("Table Grounding", f"Schema-qualified table '{node.sql()}' is not allowed")
            extracted_tables.add(table_name)
            
        # Filter out CTE aliases if any
        ctes = set()
        for cte in ast.find_all(exp.CTE):
            ctes.add(cte.alias.lower())
            
        final_tables = extracted_tables - ctes
            
        for t in final_tables:
            if t not in self.valid_tables:
                return self._fail("Table Grounding", f"Unknown table '{t}'")

        # 4. Column Grounding
        valid_columns_for_query = set()
        for t in final_tables:
            valid_columns_for_query.update(self.schema_registry[t])
            
        # Collect aliases defined in the query to avoid failing on them
        for node in ast.find_all(exp.Alias):
            alias_name = node.alias.lower()
            if alias_name:
                valid_columns_for_query.add(alias_name)
            
        for node in ast.find_all(exp.Column):
            col_name = node.name.lower()
            
            if col_name == "*":
                continue

            if col_name in self.hidden_columns:
                return self._fail("Column Grounding", f"Column '{col_name}' is not available")
                
            if col_name not in valid_columns_for_query:
                # If there are no tables queried, give a specific message
                if not final_tables:
                    return self._fail("Column Grounding", f"Unknown column '{col_name}' (No tables queried)")
                return self._fail("Column Grounding", f"Unknown column '{col_name}' in referenced tables")

        # All checks passed!
        return ValidationResult(
            is_valid=True,
            read_only=True,
            tables_valid=True,
            columns_valid=True,
            reason="Validation Passed"
        )
        
    def _fail(self, stage: str, reason: str) -> ValidationResult:
        return ValidationResult(
            is_valid=False,
            read_only=(stage != "Read-Only"),
            tables_valid=(stage != "Table Grounding"),
            columns_valid=(stage != "Column Grounding"),
            reason=f"Validation Failed [{stage}]: {reason}"
        )
