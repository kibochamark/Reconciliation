# Reconciliation System - README

## Overview
The Reconciliation System is a Django REST API that processes two CSV files (Bank Statement & Cashbook) to identify:
- Missing transactions in either file.
- Discrepancies where amounts do not match.
- A final reconciliation report in CSV, JSON, and HTML formats.

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

(Insert Process Flow Diagram Here)

---

## **Installation & Setup**
Follow these steps to set up the project:

### **1. Clone the Repository**
```bash
git clone <repository_url>
cd reconciliation-system
```

### **2. Create a Virtual Environment & Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### **3. Run Migrations**
```bash
python manage.py migrate
```

### **4. Start the Development Server**
```bash
python manage.py runserver
```

---

## **API Endpoints**
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/upload/` | Uploads two CSV files for reconciliation. |
| GET | `/results/csv/` | Returns reconciliation report in CSV format. |
| GET | `/results/json/` | Returns reconciliation report in JSON format. |
| GET | `/results/html/` | Returns reconciliation report in HTML format. |

---

## **Running Tests**
To ensure correctness, run the Django test suite:
```bash
python manage.py test
```

### **Test Coverage**
The tests cover:
- **File Upload Validation** → Ensures valid CSV files are processed.
- **Data Processing** → Checks if transactions are extracted correctly.
- **Reconciliation Logic** → Confirms missing transactions and discrepancies are detected accurately.

---

## **Contributing**
1. Fork the repository.
2. Create a new feature branch.
3. Commit and push your changes.
4. Submit a pull request.



