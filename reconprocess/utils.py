"""
Perform data normalization from dataframe
fields expected-
transaction Id
amount(debit and credit)
date
details for transactions

"""
import io
import json
import pandas as pd
from bs4 import BeautifulSoup

def data_normalization(df=None, dateformat="%Y-%m-%d"):
    try:

            # Standardize date format
            df["Transaction Date"] = pd.to_datetime(df["Transaction Date"]).dt.strftime(dateformat)


            # Convert all text to lowercase and strip whitespace
            df["Details"] = df["Details"].astype(str).str.lower().str.strip()


            # Ensure debits and credits are numeric
            df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce").fillna(0)
            df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce").fillna(0)


            # Ensure transaction IDs are consistent (removing leading zeros)
            df["Transaction ID"] = df["Transaction ID"].astype(str).str.lstrip("0")

            return df

    except Exception as e:
        print(e)







class PerformRecon:

    def __init__(self, source, target):
        self.source=source
        self.target = target


    def missing_in_target(self):
        try:

            return self.target[~self.target["Transaction ID"].isin(self.source["Transaction ID"])]

        except Exception as e:
            print(e)
            return e

    def missing_in_source(self):
        try:

            return self.source[~self.source["Transaction ID"].isin(self.target["Transaction ID"])]

        except Exception as e:
            print(e)
            return e


    def discrepancies(self):
        """
        here we are looking for any duplicated data,
        invalid transactions
        any negative values
        any transaction that does not have a corresponding debit or credit
        """
        try:
            merged_df = self.source.merge(self.target, on="Transaction ID", suffixes=("_source", "_target"))

            # Categorize discrepancies
            invalid_transactions = merged_df[(merged_df["Debit_source"] == 0) & (merged_df["Credit_source"] == 0) &
                                             (merged_df["Debit_target"] == 0) & (
                                                         merged_df["Credit_target"] == 0)].copy()
            invalid_transactions["Discrepancy Type"] = "Invalid Transaction"

            negative_values = merged_df[(merged_df["Debit_source"] < 0) | (merged_df["Credit_source"] < 0) |
                                        (merged_df["Debit_target"] < 0) | (merged_df["Credit_target"] < 0)].copy()
            negative_values["Discrepancy Type"] = "Negative Value"

            account_mismatches = merged_df[
                (~(merged_df["Debit_source"] == merged_df["Credit_target"])) &
                (~(merged_df["Credit_source"] == merged_df["Debit_target"]))
                ].copy()
            account_mismatches["Discrepancy Type"] = "Account mismatch"

            duplicates_in_source = self.source[self.source.duplicated(subset=["Transaction ID"], keep=False)].copy()
            duplicates_in_source["Discrepancy Type"] = "Duplicate in Source"

            duplicates_in_target= self.target[self.target.duplicated(subset=["Transaction ID"], keep=False)].copy()
            duplicates_in_target["Discrepancy Type"] = "Duplicate in Target"

            # Combine all discrepancies into one DataFrame
            all_discrepancies = pd.concat([
                invalid_transactions,
                negative_values,
                account_mismatches,
                duplicates_in_source,
                duplicates_in_target
            ], ignore_index=True)

            return all_discrepancies

        except Exception as e:
            print(e)
            return e




class ReportGenerator:

    def __init__(self, reporttype, json_data):
        self.reporttype = reporttype
        self.json_data = json_data  # Load JSON only once
        self.missing_source = None
        self.missing_target = None
        self.discrepancies = None
        self.convert_data_to_dataframe()





    def convert_data_to_dataframe(self):
        try:

            # print(self.json_data)

            for key, value in self.json_data.items():  # Iterate over items
                try:
                    # print(key, value)
                    records = value.get('records')
                    # print(json.loads(records), "records")# Safely get records
                    dataframe = pd.DataFrame(json.loads(records))
                    # print(type(dataframe))
                    if key == "missing_records_in_source":
                        self.missing_source = dataframe
                    elif key == "missing_records_in_target":
                        self.missing_target = dataframe
                    elif key == "discrepancies":
                        self.discrepancies = dataframe
                except (TypeError, ValueError, KeyError) as e:
                    print(f"Error processing key '{key}': {e}")


        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def to_csv(self):
        try:
            output = io.StringIO()
            combined_data = pd.DataFrame()  # Initialize an empty DataFrame

            if self.missing_source is not None:
                source_df = self.missing_source.copy()
                source_df.insert(0, 'Section', 'Missing in Source')
                combined_data = pd.concat([combined_data, source_df], ignore_index=True)

            if self.missing_target is not None:
                target_df = self.missing_target.copy()
                target_df.insert(0, 'Section', 'Missing in Target')
                combined_data = pd.concat([combined_data, target_df], ignore_index=True)

            if self.discrepancies is not None:
                discrepancies_df = self.discrepancies.copy()
                discrepancies_df.insert(0, 'Section', 'Discrepancies')
                combined_data = pd.concat([combined_data, discrepancies_df], ignore_index=True)

            combined_data.to_csv(output, index=False)
            csv_output = output.getvalue()
            return csv_output
        except AttributeError as e:
            print(f"Attribute Error in to_csv: {e}")
            return ""

    def to_json(self):
        try:
            report_data = {}
            if self.missing_source is not None:
                report_data["missing_source"] = json.loads(self.missing_source.to_json(orient='records'))
            if self.missing_target is not None:
                report_data["missing_target"] = json.loads(self.missing_target.to_json(orient='records'))
            if self.discrepancies is not None:
                report_data["discrepancies"] = json.loads(self.discrepancies.to_json(orient='records'))
            return json.dumps(report_data)  # Return the entire JSON report
        except AttributeError as e:
            print(f"Attribute Error in to_json: {e}")
            return "{}"

    def to_html(self):
        try:
            html_report = ""

            def process_dataframe(df, title):
                html = ""
                if df is not None:
                    html += f"<h2>{title}</h2>"
                    html += df.to_html(index=False)

                    # Use BeautifulSoup to minify HTML
                    soup = BeautifulSoup(html, 'html.parser')
                    html = soup.prettify()  # Prettify first for consistent parsing
                    html = "".join(line.strip() for line in html.splitlines())

                return html

            html_report += process_dataframe(self.missing_source, "Missing in Source")
            html_report += process_dataframe(self.missing_target, "Missing in Target")
            html_report += process_dataframe(self.discrepancies, "Discrepancies")

            return html_report
        except AttributeError as e:
            print(f"Attribute Error in to_html: {e}")
            return ""