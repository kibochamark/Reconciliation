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
   - Detects discrepancies in transaction amounts.
4. **Report Generation** → The system generates reconciliation results in CSV, JSON, and HTML.
5. **User Downloads Results** → The user retrieves the reports via API.

## File Format (CSV)

### Sample Files
- **[Download Sample Source CSV](https://drive.google.com/file/d/1GWB3bvnLiCLtsM3GkRIU2Y0NMlKAIYST/view?usp=sharing)**
- **[Download Sample Target CSV](https://drive.google.com/file/d/1wwYUXCRrCO6hGfiwLqm6p1GE9TMeHf1t/view?usp=sharing)**
Both source and target files should follow this structure:

| Transaction ID | Transaction Date | Details    | Debit | Credit |
|---------------|----------------|------------|-------|--------|
| 1001         | 2024-03-01      | Payment A  | 500   | 0      |
| 1002         | 2024-03-02      | Payment B  | 0     | 200    |
| 1003         | 2024-03-03      | Payment C  | -100  | 100    |

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

# Run migrations
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
-**Params:** `status` (Pending, Failed, Completed) - optional
-**Response** list of reconciled reports and their reconciliation status



## Running Tests & Coverage
```sh
# Run unit tests
python manage.py test

# Run coverage analysis
coverage run manage.py test
coverage report -m  # Show coverage report
coverage html  # Generate HTML report
```

## Limitations
- Only supports **CSV** file format.
- Transactions must have **both debit and credit** fields.
- Handles duplicates within the same dataset but may not match similar records across datasets.



---
## **Contributing**
1. Fork the repository.
2. Create a new feature branch.
3. Commit and push your changes.
4. Submit a pull request.



