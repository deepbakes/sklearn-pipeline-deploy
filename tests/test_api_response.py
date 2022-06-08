import ast
import os
import unittest

import pandas as pd
import requests
from shared_code.utils import create_report

data_dir = "../data/processed"

feature_columns = [
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "ever_married",
    "work_type",
    "residence_type",
    "avg_glucose_level",
    "bmi",
    "smoking_status",
]  # Feature columns.


class TestEqualOutputs(unittest.TestCase):
    def test_equal_predictions(self):

        """
        Test that predictions generated by create_report() are equal to Azure Function API POST request.
        """

        # Load Dataset
        df = pd.read_csv(os.path.join(data_dir, "stroke_records.csv"))
        df = df.drop(columns=feature_columns)  # Select feature columns.
        random_record = df.sample(1)  # Select random row.

        # Create Report
        analyte_names, predictions, function_report = create_report(
            input_data=random_record,
            pipeline_directory="pipelines",
            codes_dictionary_path="codes_dictionary.joblib",
        )

        function_report = [
            i for i in function_report if i
        ]  # Match format expected by Azure Function API response.

        # Create API POST Request
        col_names = list(random_record.columns)  # Feature column names.
        feature_values = random_record.values[0]  # Feature values.

        api_address = "http://localhost:7071/api/generate_report?"

        for idx, col in enumerate(col_names):
            api_address = (
                api_address + col_names[idx] + "=" + str(feature_values[idx]) + "&"
            )
        api_address = api_address[:-1]  # Remove trailing & symbol.

        resp = requests.post(api_address)  # Send request to API.
        api_report = resp.text  # Convert response to string.

        # Ensure Outputs Match
        self.assertEqual(
            function_report, ast.literal_eval(api_report)
        )  # Assert returned reports are equal.


if __name__ == "__main__":
    unittest.main()
