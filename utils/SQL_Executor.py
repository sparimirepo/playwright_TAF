# utils/sql_executor.py

class SQLExecutor:
    def __init__(self, connection):
        self.conn = connection

    def execute_query(self, sql_query):
        """
        Execute a read-only SQL query (e.g., SELECT) and return results.

        Args:
            sql_query (str): SQL query string.

        Returns:
            list of tuples: Query result rows.
        """
        cursor = self.conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        cursor.close()
        return results
