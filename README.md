# FAi – Freelance Automation Italia 🇮🇹

**FAi** (Freelance Automation Italia) is an all-in-one platform designed to help Italian freelancers manage their day-to-day operations: 
from invoices to calendar bookings, automated email handling, and digital invoicing via SDI/PEC.

> Built with Python, Streamlit, SQLite, and love from the UK and Italy

---

## 🚀 Features

- **Invoice Management**
  - Create invoices with VAT and auto-calculated totals
  - Export invoices as stylish PDFs
  - Track invoices in an archive by year and month
  - Automatically generate electronic invoices (FatturaPA) in XML
  - Validate XML against Italian government schema
  - Send via certified email (PEC) to the *Sistema di Interscambio* (SDI)

- **Client CRM**
  - Add, update and organize client profiles
  - Search, sort, and group alphabetically
  - Associate clients with invoice history

- **Calendar**
  - Book and visualize appointments
  - Set reminders and sync with client records

- **Automation (Coming Soon)**
  - Auto-email follow-ups
  - Auto-generate recurring invoices
  - Backup/export to cloud

---

## 🛠 Tech Stack

- [Python 3.11+](https://www.python.org/)
- [Streamlit](https://streamlit.io/) for the UI
- [SQLite](https://www.sqlite.org/index.html) for local storage
- [lxml](https://lxml.de/) for XML/XSD validation
- SMTP/PEC integration for email and SDI transmission

---

## 📦 Getting Started

```bash
git clone https://github.com/yourusername/freelanceDashboard.git
cd freelanceDashboard
pip install -r requirements.txt
streamlit run app.py
```
---

> You'll find all app modules under /modules, utilities in /utils, and XML templates under /invoices_xml.

---
### ✅ **Status**
This MVP is under active development and currently supports:

Invoice creation + PDF

FatturaPA XML generation and validation

PEC transmission via preconfigured providers (Aruba, PosteCert, Legalmail)

CRM with grouped client list

---
### 💡 **Roadmap Highlights**
Week 1 (Done): Invoicing system + SDI integration

Week 2: Client CRM + Calendar module

Week 3: Event scheduling + reminder logic

Week 4: Onboarding + multi-user login

September: Premium features + automations

---
### 🛡 **Legal & Compliance**
FAi is designed to be compliant with Italian invoicing laws, including:

FatturaPA format (XML 1.2.3)

PEC integration for SDI

Local client-side storage (SQLite)

Use responsibly and consult with a fiscal advisor if needed.

---
### ✨ Credits
Developed by Stefano
Inspired by the needs of Italian freelancers.
Made in the UK with Italian passion 🇮🇹
