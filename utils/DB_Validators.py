# utils/db_validators.py

import os
from utils.SQL_Executor import SQLExecutor

# List of form fields that represent multi-select checkbox values stored in DB as semicolon-separated strings
MULTI_SELECT_FIELDS = ['DataSource']  # Add other multi-select field names here as needed

def validate_data_in_db(db_connection, form_data: dict, sql_file_path: str, expected_columns: list):

    sql_executor = SQLExecutor(db_connection)

    # Read SQL template from file
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql_template = f.read()

    # Escape single quotes in form_data values for safe SQL substitution
    safe_data = {
        k: str(v).replace("'", "''") if v is not None else ''
        for k, v in form_data.items()
    }

    # Format SQL query by substituting placeholders with sanitized values
    sql_query = sql_template.format(**safe_data)

    results = sql_executor.execute_query(sql_query)
    assert results, f"No records returned for SQL: {sql_file_path} with form data: {form_data}"

    db_row = results[0]

    for idx, col in enumerate(expected_columns):
        expected = form_data.get(col)
        actual = db_row[idx]

        if col in MULTI_SELECT_FIELDS:
            # Handle multi-select values stored as semicolon-separated strings.
            # Split actual DB string into list and strip spaces.
            actual_list = [item.strip() for item in actual.split(';')] if actual else []

            # Check all expected values are present in actual DB list
            missing = [item for item in expected if item not in actual_list] if expected else []
            assert not missing, (
                f"Missing values in DB for multi-select field '{col}': {missing}"
            )
        else:
            assert actual == expected, (
                f"Value mismatch for field '{col}': expected '{expected}', got '{actual}'"
            )
