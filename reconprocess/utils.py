"""
Perform data normalization from dataframe
fields expectec--
transaction Id
amount
date
details fof transactions

"""
import json

import pandas as pd


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
        here we are looking for any duplicated data or erroneous data
        """
        try:
            merged_df = self.source.merge(self.target, on="Transaction ID", suffixes=("_source", "_target"))
            discrepancies = merged_df[
                (merged_df["Debit_source"] != merged_df["Debit_target"]) |
                (merged_df["Credit_source"] != merged_df["Credit_target"])
            ]

            # Identify duplicate transactions in source
            duplicate_in_source = self.source[self.source.duplicated(subset=["Transaction ID"], keep=False)]

            # Identify duplicate transactions in target
            duplicate_in_target = self.target[self.target.duplicated(subset=["Transaction ID"], keep=False)]



            # Add duplicates to discrepancies report
            discrepancies = pd.concat([discrepancies, duplicate_in_source, duplicate_in_target]).drop_duplicates().reset_index(drop=True)



            return discrepancies

        except Exception as e:
            print(e)
            return e




class ReportGenerator:


    def __int__(self, reporttype, json_data):
        self.reporttype=reporttype
        self.json_data = json_data
        self.dataframe = None
        self.convert_data_to_dataframe()


    def convert_data_to_dataframe(self):

        try:
            load_json= json.loads(self.json_data)

            dataframe= pd.DataFrame(load_json.get("records"))
            self.dataframe = dataframe


            print(type(dataframe), "df")

        except Exception as e:
            print(e)
            return e

    def to_csv(self):

        return self.dataframe.to_csv()


    def to_json(self):

        return self.dataframe.to_json()


    def to_html(self):

        return self.dataframe.to_html()

