import oracledb

from utils.logging.logger_utils import log_step, capture_and_log_failure


class ADW_Util:
    def __init__(self, wallet_path: str, tns_alias: str, user: str, password: str):
        log_step('DB_Util construction execution started..!')
        self.wallet_path = wallet_path
        self.tns_alias = tns_alias
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        try:
            log_step("Attempting to connect NextGen ADW")
            #oracledb.init_oracle_client(config_dir=str(self.wallet_path))
            self.connection = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=self.tns_alias,
                config_dir=self.wallet_path,
                wallet_location=self.wallet_path,
                wallet_password="Prima123Vera"
            )
            log_step("Connected to NextGen ADW Database")
        except Exception as e:
            log_step("Failed to Connect to NextGen ADW Database")
            capture_and_log_failure(page = None, step_name="ADW Connection is failing.. from DB Util class..!")
            raise ConnectionError(f"❌Failed to Connect to NextGen ADW Database: {e}")

    def get_DB_Object(self):
        if not self.connection:
            raise ConnectionError("Database object is not created and please check DB Connection..!")
        return self.connection

    def close_db_connection(self):
        if self.connection:
            try:
                self.connection.close()
                log_step("🔒Database connection is closed")

            except Exception as e:
                log_step(f"Not able to close DB Connection: {e}")

    def executeQuery(self, query, params=None):
        cursor = None
        try:
            log_step(f"Query received to execute: {query}")
            cursor = self.connection.cursor()

            cursor.execute(query, params or {})

            # If SELECT query, fetch results
            if query.strip().lower().startswith("select"):
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows]
                return result
            else:
                self.connection.commit()
                return cursor.rowcount  # number of rows affected

        except Exception as e:
            log_step(f"❌ Error executing query: {e}")
            raise

        finally:
            if cursor:
                cursor.close()

