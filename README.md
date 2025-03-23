# Reconciliation System

## Overview
The Reconciliation System is a Django REST API that processes two CSV files (Source & Target) to identify:
- Missing transactions in either file.
- Discrepancies where amounts do not match.
- A final reconciliation report in CSV, JSON, and HTML formats.

## Features
- **Upload Source & Target Files** (CSV format)
- **Identify missing transactions**
- **Detect discrepancies** (account mismatches, invalid entries, duplicates, etc.)
- **Generate Reports** in JSON, CSV, and HTML formats
- **Unit tests with test coverage**
- **Gemini Implementation for Discrepancy Detection**: Uses the Gemini algorithm to enhance the accuracy of identifying discrepancies between the two files, by implementing advanced comparison logic based on predefined matching rules.

## **Process Flow**
Below is the high-level process flow of the reconciliation system:

1. **User Uploads CSV Files** → The user uploads a source file (Bank Statement) and a target file (Cashbook) via an API request.
2. **Data Normalization** → The system cleans and formats the data:
   - Ensures date formats are standardized.
   - Removes extra spaces and converts text to lowercase.
   - Converts debit/credit amounts into a single format.
3. **Reconciliation Process** → The system compares both files and:
   - Identifies transactions missing in the Cashbook.
   - Identifies transactions missing in the Bank Statement.
   - Detects discrepancies in transaction amounts using **Gemini**: The Gemini implementation applies an algorithm to detect even the smallest discrepancies, ensuring accurate reconciliation.
4. **Report Generation** → The system generates reconciliation results in CSV, JSON, and HTML.
5. **User Downloads Results** → The user retrieves the reports via API.

## File Format (CSV)

### Sample Files
Here are some sample files for testing the reconciliation process:

- **[Download Sample Source CSV](https://drive.google.com/file/d/1GWB3bvnLiCLtsM3GkRIU2Y0NMlKAIYST/view?usp=sharing)**
- **[Download Sample Target CSV](https://drive.google.com/file/d/1wwYUXCRrCO6hGfiwLqm6p1GE9TMeHf1t/view?usp=sharing)**
- **[Download Sample Kaggle Source CSV](https://drive.google.com/file/d/1gYnXOuUbTfUZQOOXOG9Mj3pTSYjzyNbr/view?usp=sharing)** (Kaggle Source file)
- **[Download Sample Kaggle Target CSV](https://drive.google.com/file/d/1rgX9wE7p25OekMNDIoEuJyC-_vtx-1qE/view?usp=sharing)** (Kaggle Target file)

Both source and target files should follow this structure:

| Transaction ID | Transaction Date | Details    | Debit | Credit |
|---------------|------------------|------------|-------|--------|
| 1001          | 2024-03-01       | Payment A  | 500   | 0      |
| 1002          | 2024-03-02       | Payment B  | 0     | 200    |
| 1003          | 2024-03-03       | Payment C  | -100  | 100    |

## Installation
```sh
# Clone the repository
git clone https://github.com/kibochamark/Reconciliation.git
cd reconciliation-system

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Rename sample env file to .env
#Copy the app secret keys from the link below and paste them into the .env file.
# Make sure to replace placeholder values in the sample.env with actual values.
[Download App Secret Keys](https://docs.google.com/document/d/1JsscC0l5HU5hhhMX2_G6KXeiX1_TgODm978XJgVdKj8/edit?usp=sharing)


# Update the .env file accordingly

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

## Running the API
```sh
# Start the server
python manage.py runserver
```
The API will be available at: `http://127.0.0.1:8000/`

## API Endpoints
### 1. Upload CSV Files
**POST** `/api/v1/recon/upload`
- **Request:** `source_file` and `target_file` (CSV files)
- **Response:** Returns a `task_id` for reference.

### 2. Generate Reconciliation Report
**POST** `/api/v1/recon/generate_report`
- **Request:** `report_type` (JSON, CSV, HTML) & `report_task_id`
- **Response:** The requested report.

### 3. List of Reconciliation Tasks
**GET** `/api/v1/recon/tasks`
- **Params:** `status` (Pending, Failed, Completed) - optional
- **Response:** List of reconciled reports and their reconciliation status.

## Running Tests & Coverage
```sh
# Run unit tests
python manage.py test

# Run coverage analysis
coverage run manage.py test
coverage report -m  # Show coverage report
coverage html  # Generate HTML report
```

### Coverage Report

Below is the current test coverage report for the project:

```
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
manage.py                                    11      2    82%   12-13
recon\__init__.py                             0      0   100%
recon\settings.py                            25      0   100%
recon\urls.py                                 4      0   100%
reconprocess\__init__.py                      0      0   100%
reconprocess\admin.py                         5      0   100%
reconprocess\apps.py                          4      0   100%
reconprocess\filterset.py                    11      0   100%
reconprocess\migrations\0001_initial.py       6      0   100%
reconprocess\migrations\__init__.py           0      0   100%
reconprocess\models.py                       30      4    87%   8, 11, 34, 51
reconprocess\serializers.py                  32      0   100%
reconprocess\tests.py                        77      0   100%
reconprocess\urls.py                          3      0   100%
reconprocess\utils.py                       144     38    74%   42-46, 67-69, 76-78, 124-126, 173-174, 207, 209, 212-218, 227-229, 232-234, 244-246, 252, 254, 258-260, 284-286
reconprocess\views.py                        98     21    79%   40-48, 78, 127-147, 173-177, 201, 207, 246, 258-259
-----------------------------------------------------------------------
TOTAL                                       450     65    86%
```

## Limitations
- Only supports **CSV** file format.
- Transactions must have **both debit and credit** fields.
- Handles duplicates within the same dataset but may not match similar records across datasets.
- The Gemini algorithm is designed to improve matching accuracy but may still encounter edge cases in complex discrepancies.

## **Postman API Documentation**
For detailed information about the API endpoints, parameters, and examples, please refer to the [Postman API Documentation](https://documenter.getpostman.com/view/36984250/2sAYkHodNH).

## **Contributing**
1. Fork the repository.
2. Create a new feature branch.
3. Commit and push your changes.
4. Submit a pull request.

