import json

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile

import pandas as pd
import io

from reconprocess.utils import data_normalization, PerformRecon


class ReconciliationTestCase(TestCase):
    def setUp(self):
        """Set up test files and sample data."""
        self.client = Client()

        # Create test CSV data
        self.source_csv = SimpleUploadedFile(
            "source.csv",
            b"Transaction ID,Transaction Date,Details,Debit,Credit\n"
            b"1001,2024-03-01,Payment A,500,0\n"
            b"1002,2024-03-02,Payment B,0,200\n"
            b"1003,2024-03-03,Payment C,-100,100\n"  # Negative debit
            b"1004,2024-03-04,Payment D,200,0\n",
            content_type="text/csv"
        )

        self.target_csv = SimpleUploadedFile(
            "target.csv",
            b"Transaction ID,Transaction Date,Details,Debit,Credit\n"
            b"1001,2024-03-01,Payment A,0,500\n"
            b"1002,2024-03-02,Payment B,200,0\n"
            b"1003,2024-03-03,Payment C,100,0\n"  # Mismatched credit
            b"1005,2024-03-05,Payment E,300,0\n",
            content_type="text/csv"
        )






    def test_file_upload_valid_csv(self):
        """Test if valid CSV files are accepted."""
        response = self.client.post("/api/v1/recon/upload", {"source_file": self.source_csv, "target_file": self.target_csv})
        self.assertEqual(response.status_code, 201)
        # print(response.json()['id'])
        self.assertIn("completed", response.json()["status"])
        return response.json()['id']




    def test_missing_transactions_in_source(self):
        """Test if reconciliation detects missing transactions."""
        source_df = pd.read_csv(io.BytesIO(self.source_csv.read()))
        target_df = pd.read_csv(io.BytesIO(self.target_csv.read()))

        # normalize data
        normalize_source = data_normalization(source_df)
        normalize_target = data_normalization(target_df)

        # instantiate the Recon class  and pass our normalized data
        recon = PerformRecon(normalize_source, normalize_target)

        self.assertEqual(len(recon.missing_in_source()), 1)



    def test_missing_transactions_in_target(self):
        """Test if reconciliation detects missing transactions."""
        source_df = pd.read_csv(io.BytesIO(self.source_csv.read()))
        target_df = pd.read_csv(io.BytesIO(self.target_csv.read()))
        # normalize data
        normalize_source = data_normalization(source_df)
        normalize_target = data_normalization(target_df)

        # instantiate the Recon class  and pass our normalized data
        recon = PerformRecon(normalize_source, normalize_target)

        self.assertEqual(len(recon.missing_in_target()), 1)

    def test_reconciliation_discrepant_transactions(self):
        """Test if reconciliation detects missing transactions."""
        source_df = pd.read_csv(io.BytesIO(self.source_csv.read()))
        target_df = pd.read_csv(io.BytesIO(self.target_csv.read()))

        # normalize data
        normalize_source = data_normalization(source_df)
        normalize_target = data_normalization(target_df)

        # instantiate the Recon class  and pass our normalized data
        recon = PerformRecon(normalize_source, normalize_target)


        # Get discrepancies
        discrepancies = recon.discrepancies()

        # Convert DataFrame to list of dictionaries
        discrepancies = discrepancies.to_dict(orient="records")

        # Ensure discrepancies is a list
        self.assertIsInstance(discrepancies, list, "Discrepancies should be a list")

        # Extract discrepancy types
        expected_types = {"Duplicate in Target", "Duplicate in Source", "Invalid Transaction", "Account Mismatch",
                          "Negative Value"}
        found_types = {d.get("Discrepancy Type", "") for d in discrepancies}  # Use .get() to avoid key errors


        # Ensure at least one expected discrepancy exists
        self.assertTrue(expected_types & found_types, "Expected discrepancy types were not found")

        # Check expected number of discrepancies (adjust count based on dataset)
        self.assertGreaterEqual(len(discrepancies), 1, "Expected at least one discrepancy")


    def test_invalid_file_type(self):
        """Test rejection of non-CSV files."""
        response = self.client.post("/api/v1/recon/upload", {"source_file": SimpleUploadedFile("invalid.txt", b"Hello World"),
                                                 "target_file": self.target_csv})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_result_generation_json(self):
        """Test if reconciliation results are correctly returned in JSON format."""

        recon=self.test_file_upload_valid_csv()
        print(recon)

        response = self.client.post("/api/v1/recon/generate_report", {"report_type": "JSON", "report_task_id": recon})
        # print(response["Content-Type"], response.status_code, response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/json"))
    #
    def test_result_generation_csv(self):
        """Test if reconciliation results are correctly returned in CSV format."""
        recon = self.test_file_upload_valid_csv()
        # print(recon)
        response = self.client.post("/api/v1/recon/generate_report", {"report_type": "CSV", "report_task_id": recon})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
    #
    def test_result_generation_html(self):
        """Test if reconciliation results are correctly returned in HTML format."""
        recon = self.test_file_upload_valid_csv()
        # print(recon)
        response = self.client.post("/api/v1/recon/generate_report", {"report_type": "HTML", "report_task_id": recon})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/html"))



