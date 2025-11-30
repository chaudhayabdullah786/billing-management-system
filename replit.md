# Grocery Store Billing Management System

## Overview
A comprehensive full-stack grocery billing system built with Flask, featuring a modern POS interface, inventory management, customer tracking, invoice generation with PDF export, and analytics dashboard.

## Project Structure
```
/
├── app.py                 # Main Flask application with all routes
├── config.py              # Application configuration
├── models.py              # SQLAlchemy database models
├── pdf_generator.py       # ReportLab PDF invoice generator
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base layout with sidebar navigation
│   ├── login.html         # Login page
│   ├── dashboard.html     # Analytics dashboard
│   ├── pos.html           # Point of Sale billing interface
│   ├── products.html      # Product listing
│   ├── add_product.html   # Add new product form
│   ├── edit_product.html  # Edit product form
│   ├── import_products.html # CSV import
│   ├── customers.html     # Customer listing
│   ├── add_customer.html  # Add customer form
│   ├── view_customer.html # Customer details with purchase history
│   ├── invoices.html      # Invoice listing
│   ├── view_invoice.html  # Invoice details
│   ├── inventory.html     # Inventory management
│   ├── reports.html       # Reports and analytics
│   ├── users.html         # User management
│   ├── add_user.html      # Add user form
│   └── activity_logs.html # Activity logs
├── static/
│   ├── css/style.css      # Custom styles
│   └── js/
│       ├── main.js        # Main JavaScript utilities
│       └── pos.js         # POS/billing functionality
└── requirements.txt       # Python dependencies
```

## Key Features
1. **Authentication**: Role-based access (Admin/Cashier)
2. **Product Management**: CRUD operations, CSV import, barcode generation
3. **Customer Management**: Customer profiles, purchase history tracking
4. **POS Billing**: Modern cart interface, barcode/name search, tax/discount
5. **Invoice System**: PDF generation, search, reprint
6. **Inventory**: Auto stock deduction, low-stock alerts, stock valuation
7. **Analytics Dashboard**: Charts for sales trends, top products
8. **Activity Logging**: Admin action tracking

## Default Credentials
- **Admin**: username: `admin`, password: `admin123`
- **Cashier**: username: `cashier`, password: `cashier123`

## Database
PostgreSQL with SQLAlchemy ORM. Tables:
- users, categories, products, customers, invoices, invoice_items, activity_logs

## API Endpoints
- `GET /api/products` - List all products
- `GET /api/products/search?q=` - Search products
- `GET /api/customers` - List customers
- `GET /api/customers/search?q=` - Search customers
- `POST /api/invoice/create` - Create new invoice
- `GET /api/invoice/<id>` - Get invoice details
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/reports/export?type=` - Export reports as CSV

## Technology Stack
- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, Chart.js, jQuery
- **Database**: PostgreSQL
- **PDF Generation**: ReportLab

## Recent Changes
- Initial project setup (Nov 2025)
