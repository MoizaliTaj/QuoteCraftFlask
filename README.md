# QuoteCraftFlask
# This Web Application was designed to prepare quotations.

```markdown
# Steps to launch the app

## Setup
1. Navigate into the directory.
2. Run the following commands:

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python main.py
```

## User Details
Currently, there are 2 users in the application:

- Username: admin, Password: Pass@1234 (Admin rights)
- Username: user, Password: Pass@1234

## Steps to create a quotation

After logging in, you can create quotations for customers. If it's the first time creating a quotation for a customer, you need to add the customer and then add an invoice to it.

When adding items to an invoice, there are currently 10 dummy product entries in the app. (The actual application will have thousands of product entries.) You can use any of the below dummy codes to add a product to a quotation:

- CODE1
- CODE2
- CODE3
- CODE4
- CODE5
- CODE6
- CODE7
- CODE8
- CODE9
- CODE10

## Features

### Overview
- Profit margin information for overall quotation and when adding or editing individual items.
- Display of similar quotation history for the customer when adding a new item.
- Separate section to check the history of a customer.
- Various quotation print modes available.
- Logs to track changes done by different users.
```

