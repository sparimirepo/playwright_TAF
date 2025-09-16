import yaml

class YamlLoader:
    @staticmethod
    def load_yaml(yaml_path):
        """
        Loads data from a YAML file and returns it as a Python dictionary.
        
        Args:
            yaml_path (str): Path to the YAML file.
        
        Returns:
            dict: Data loaded from the YAML file.
        """
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_test_data_for_class(test_class_name: str, data_key: str):
        """
        Loads all test data entries under a specified key from all YAML files mapped in testData_Mapping.yaml
        for the given test class.

        Args:
            test_class_name (str): The lowercase name of the test class to load data for.
            data_key (str): The key inside the YAML files to extract data from.

        Returns:
            list: List of data dictionaries for tests.
        """
        with open("testData/testData_Mapping.yaml", "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
        data_files = manifest.get('test_classes', {}).get(test_class_name.lower(), {}).get('data_files', [])
        
        data_entries = []
        for file_path in data_files:
            data = YamlLoader.load_yaml(file_path)
            data_entries.extend(data.get(data_key, []))
        return data_entries


    @staticmethod
    def get_sql_files_for_class(test_class_name: str):
        """
        Returns a list of SQL file paths for the given test class,
        based on testData_Mapping.yaml.

        Args:
            test_class_name (str): Lowercase name of the test class.

        Returns:
            list: List of SQL file paths.
        """
        with open("testData/testData_Mapping.yaml", "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
        sql_files = manifest.get('test_classes', {}).get(test_class_name.lower(), {}).get('sql_files', [])
        return sql_files

    @staticmethod
    def load_sql_file(sql_path):
        """
        Loads and returns the contents of a SQL file as a string.

        Args:
            sql_path (str): Path to the .sql file.

        Returns:
            str: The SQL query/queries as a string.
        """
        with open(sql_path, 'r', encoding='utf-8') as f:
            return f.read()


