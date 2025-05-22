import sqlite3


class FunctionalContextDatabase:
    def __init__(self):
        self._conn = sqlite3.connect("docgen.db")
        self._cursor = self._conn.cursor()

        # Create table for generated documentation
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documentation (
                function_name TEXT PRIMARY KEY,
                file_path TEXT,
                start_line INTEGER,
                end_line INTEGER,
                docstring TEXT
            )
        """
        )
