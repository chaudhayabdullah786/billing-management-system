# 🛒 Billing Management System – Python (Flask + SQLAlchemy)

A complete **Grocery Store Billing & Inventory Management System** built using **Python, Flask, SQLAlchemy, HTML/CSS, and JavaScript**.  
This system allows store owners to manage inventory, generate customer bills, create PDF invoices, track products, and handle store operations efficiently.

This project also supports **Pakistani Rupee (PKR)** currency and is fully deployable on **Replit**, **PythonAnywhere**, or **local servers**.

---

## 🚀 Features

### 🧾 **Billing System**
- Create customer bills
- Real-time price calculation
- Auto total, tax, discount, and net payable amount
- PDF invoice generation using `pdf_generator.py`

---

### 📦 **Inventory Management**
- Add new grocery products  
- Update prices  
- Manage stock quantity  
- Bulk upload (hundreds of products available)

---

### 🧮 **Store Operations**
- Product search  
- Category management  
- Automatic price updates  
- Pakistani currency formatting (PKR)

---

### 🛡️ **Admin Panel**
- Configurable default credentials  
- Secure login  
- Session-based authorization  

---

### 🧪 **API Support**
- REST API included (`postman_collection.json`)
- CRUD API for inventory & billing
- Automated tests (`test_api.py`)

---

## 📂 Project Structure

```
Billing-Management-System/
│
├── app.py
├── main.py
├── config.py
├── models.py
├── pdf_generator.py
├── test_api.py
│
├── static/
├── templates/
├── attached_assets/
│
├── requirements.txt
├── pyproject.toml
├── uv.lock
│
├── DEPLOYMENT.md
├── replit.md
└── README.md
```

---

## 🧰 Tech Stack

### **Backend**
- Python  
- Flask  
- SQLAlchemy  
- ReportLab (for PDF generation)

### **Frontend**
- HTML  
- CSS  
- JavaScript  
- Bootstrap (if enabled in templates)

### **Database**
- SQLite (default)  
- MySQL / PostgreSQL supported via SQLAlchemy

---

## 🏁 How to Run Locally

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Run the application
```bash
python main.py
```

### 3️⃣ Open in browser
```
http://127.0.0.1:5000/
```

---

## 🧪 Running Tests
```bash
pytest test_api.py
```

---

## 📄 Deployment Guides
Deployment instructions available in:

- `DEPLOYMENT.md`  
- `replit.md`  

Supports:
- Replit  
- PythonAnywhere  
- Local Server  
- Gunicorn (with minor tweaks)

---

## 📸 Screenshots (Optional)
If you want, I can generate preview images and add them here.

---

## 🎯 Project Highlights
- Fully working store billing system  
- Complete CRUD for products  
- Auto-generation of PDF invoices  
- Optimized for grocery stores  
- Real products dataset included  
- Pakistani rupee support  
- Can be used by small/medium shop owners  

---

## 📬 Need a Better README?

I can add:
- Badges  
- GIF demo  
- Screenshots section  
- API documentation section  
- Deployment badge  

Just tell me! 
