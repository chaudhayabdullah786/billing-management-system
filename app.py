from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import io
import os

from config import Config
from models import db, User, Product, Category, Customer, Invoice, InvoiceItem, ActivityLog, log_activity
from pdf_generator import generate_invoice_pdf

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@grocery.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            cashier = User(
                username='cashier',
                email='cashier@grocery.com',
                role='cashier'
            )
            cashier.set_password('cashier123')
            db.session.add(cashier)
            
            categories = [
                Category(name='Fruits & Vegetables', description='Fresh produce'),
                Category(name='Dairy Products', description='Milk, cheese, butter, eggs'),
                Category(name='Beverages', description='Drinks and juices'),
                Category(name='Snacks', description='Chips, cookies, nuts'),
                Category(name='Grocery Staples', description='Rice, flour, oil, spices'),
                Category(name='Personal Care', description='Soap, shampoo, toiletries'),
                Category(name='Household', description='Cleaning supplies'),
                Category(name='Frozen Foods', description='Frozen items'),
            ]
            for cat in categories:
                db.session.add(cat)
            
            db.session.commit()
            
            sample_products = [
                {'name': 'Apple (1 kg)', 'category': 'Fruits & Vegetables', 'price': 150, 'quantity': 100},
                {'name': 'Banana (1 dozen)', 'category': 'Fruits & Vegetables', 'price': 60, 'quantity': 80},
                {'name': 'Tomato (1 kg)', 'category': 'Fruits & Vegetables', 'price': 40, 'quantity': 120},
                {'name': 'Milk (1 L)', 'category': 'Dairy Products', 'price': 55, 'quantity': 200},
                {'name': 'Butter (500g)', 'category': 'Dairy Products', 'price': 250, 'quantity': 50},
                {'name': 'Cheese (200g)', 'category': 'Dairy Products', 'price': 180, 'quantity': 40},
                {'name': 'Orange Juice (1 L)', 'category': 'Beverages', 'price': 120, 'quantity': 60},
                {'name': 'Cola (2 L)', 'category': 'Beverages', 'price': 85, 'quantity': 100},
                {'name': 'Potato Chips (200g)', 'category': 'Snacks', 'price': 50, 'quantity': 150},
                {'name': 'Cookies (300g)', 'category': 'Snacks', 'price': 80, 'quantity': 80},
                {'name': 'Rice (5 kg)', 'category': 'Grocery Staples', 'price': 350, 'quantity': 70},
                {'name': 'Cooking Oil (1 L)', 'category': 'Grocery Staples', 'price': 180, 'quantity': 90},
                {'name': 'Wheat Flour (1 kg)', 'category': 'Grocery Staples', 'price': 45, 'quantity': 100},
                {'name': 'Shampoo (200ml)', 'category': 'Personal Care', 'price': 150, 'quantity': 60},
                {'name': 'Soap (100g)', 'category': 'Personal Care', 'price': 35, 'quantity': 200},
            ]
            
            for p in sample_products:
                cat = Category.query.filter_by(name=p['category']).first()
                product = Product(
                    name=p['name'],
                    barcode=Product.generate_barcode(),
                    category_id=cat.id if cat else None,
                    price=p['price'],
                    cost_price=p['price'] * 0.7,
                    quantity=p['quantity']
                )
                db.session.add(product)
            
            walk_in = Customer(
                name='Walk-in Customer',
                mobile='0000000000',
                email='walkin@grocery.com'
            )
            db.session.add(walk_in)
            
            db.session.commit()
            print("Database initialized with sample data!")

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'error')
                return render_template('login.html')
            
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_activity(user.id, 'LOGIN', f'User logged in', request.remote_addr)
            
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'LOGOUT', 'User logged out', request.remote_addr)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_start = today.replace(day=1)
    
    today_sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
        db.func.date(Invoice.created_at) == today
    ).scalar() or 0
    
    weekly_sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
        db.func.date(Invoice.created_at) >= week_ago
    ).scalar() or 0
    
    monthly_sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
        db.func.date(Invoice.created_at) >= month_start
    ).scalar() or 0
    
    today_invoices = Invoice.query.filter(
        db.func.date(Invoice.created_at) == today
    ).count()
    
    total_products = Product.query.filter_by(is_active=True).count()
    low_stock_count = Product.query.filter(
        Product.is_active == True,
        Product.quantity <= Config.LOW_STOCK_THRESHOLD
    ).count()
    
    total_customers = Customer.query.count()
    
    low_stock_products = Product.query.filter(
        Product.is_active == True,
        Product.quantity <= Config.LOW_STOCK_THRESHOLD
    ).order_by(Product.quantity.asc()).limit(10).all()
    
    recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(10).all()
    
    recent_activities = ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()
    
    return render_template('dashboard.html',
        today_sales=float(today_sales),
        weekly_sales=float(weekly_sales),
        monthly_sales=float(monthly_sales),
        today_invoices=today_invoices,
        total_products=total_products,
        low_stock_count=low_stock_count,
        total_customers=total_customers,
        low_stock_products=low_stock_products,
        recent_invoices=recent_invoices,
        recent_activities=recent_activities
    )

@app.route('/pos')
@login_required
def pos():
    products = Product.query.filter_by(is_active=True).filter(Product.quantity > 0).all()
    categories = Category.query.all()
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('pos.html', products=products, categories=categories, customers=customers)

@app.route('/products')
@login_required
def products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    
    query = Product.query
    
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search}%'),
                Product.barcode.ilike(f'%{search}%')
            )
        )
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products = query.order_by(Product.name).paginate(page=page, per_page=20)
    categories = Category.query.all()
    
    return render_template('products.html', products=products, categories=categories, search=search, selected_category=category_id)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        price = request.form.get('price')
        cost_price = request.form.get('cost_price', 0)
        quantity = request.form.get('quantity', 0)
        unit = request.form.get('unit', 'piece')
        description = request.form.get('description', '')
        
        barcode = request.form.get('barcode') or Product.generate_barcode()
        
        if Product.query.filter_by(barcode=barcode).first():
            flash('Barcode already exists!', 'error')
            return redirect(url_for('add_product'))
        
        product = Product(
            name=name,
            barcode=barcode,
            category_id=category_id if category_id else None,
            price=Decimal(price),
            cost_price=Decimal(cost_price) if cost_price else 0,
            quantity=int(quantity),
            unit=unit,
            description=description
        )
        
        db.session.add(product)
        db.session.commit()
        
        log_activity(current_user.id, 'PRODUCT_ADD', f'Added product: {name}', request.remote_addr)
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    
    categories = Category.query.all()
    return render_template('add_product.html', categories=categories)

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.category_id = request.form.get('category_id') or None
        product.price = Decimal(request.form.get('price'))
        product.cost_price = Decimal(request.form.get('cost_price', 0))
        product.quantity = int(request.form.get('quantity', 0))
        product.unit = request.form.get('unit', 'piece')
        product.description = request.form.get('description', '')
        product.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        
        log_activity(current_user.id, 'PRODUCT_EDIT', f'Edited product: {product.name}', request.remote_addr)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))
    
    categories = Category.query.all()
    return render_template('edit_product.html', product=product, categories=categories)

@app.route('/products/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    product.is_active = False
    db.session.commit()
    
    log_activity(current_user.id, 'PRODUCT_DELETE', f'Deleted product: {product.name}', request.remote_addr)
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products'))

@app.route('/products/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_products():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded!', 'error')
            return redirect(url_for('import_products'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('import_products'))
        
        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file!', 'error')
            return redirect(url_for('import_products'))
        
        try:
            stream = io.StringIO(file.stream.read().decode('UTF8'), newline=None)
            reader = csv.DictReader(stream)
            
            imported = 0
            for row in reader:
                category = None
                if 'category' in row and row['category']:
                    category = Category.query.filter_by(name=row['category']).first()
                    if not category:
                        category = Category(name=row['category'])
                        db.session.add(category)
                        db.session.flush()
                
                barcode = row.get('barcode') or Product.generate_barcode()
                if Product.query.filter_by(barcode=barcode).first():
                    barcode = Product.generate_barcode()
                
                product = Product(
                    name=row['name'],
                    barcode=barcode,
                    category_id=category.id if category else None,
                    price=Decimal(row.get('price', 0)),
                    cost_price=Decimal(row.get('cost_price', 0)),
                    quantity=int(row.get('quantity', 0)),
                    unit=row.get('unit', 'piece'),
                    description=row.get('description', '')
                )
                db.session.add(product)
                imported += 1
            
            db.session.commit()
            log_activity(current_user.id, 'PRODUCT_IMPORT', f'Imported {imported} products', request.remote_addr)
            flash(f'Successfully imported {imported} products!', 'success')
            return redirect(url_for('products'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error importing file: {str(e)}', 'error')
            return redirect(url_for('import_products'))
    
    return render_template('import_products.html')

@app.route('/customers')
@login_required
def customers():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Customer.query
    
    if search:
        query = query.filter(
            db.or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.mobile.ilike(f'%{search}%')
            )
        )
    
    customers = query.order_by(Customer.name).paginate(page=page, per_page=20)
    
    return render_template('customers.html', customers=customers, search=search)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        email = request.form.get('email', '')
        address = request.form.get('address', '')
        
        if Customer.query.filter_by(mobile=mobile).first():
            flash('Customer with this mobile number already exists!', 'error')
            return redirect(url_for('add_customer'))
        
        customer = Customer(
            name=name,
            mobile=mobile,
            email=email,
            address=address
        )
        
        db.session.add(customer)
        db.session.commit()
        
        log_activity(current_user.id, 'CUSTOMER_ADD', f'Added customer: {name}', request.remote_addr)
        flash('Customer added successfully!', 'success')
        return redirect(url_for('customers'))
    
    return render_template('add_customer.html')

@app.route('/customers/<int:id>')
@login_required
def view_customer(id):
    customer = Customer.query.get_or_404(id)
    invoices = Invoice.query.filter_by(customer_id=id).order_by(Invoice.created_at.desc()).all()
    return render_template('view_customer.html', customer=customer, invoices=invoices)

@app.route('/invoices')
@login_required
def invoices():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = Invoice.query
    
    if search:
        query = query.join(Customer, isouter=True).filter(
            db.or_(
                Invoice.invoice_number.ilike(f'%{search}%'),
                Customer.name.ilike(f'%{search}%'),
                Customer.mobile.ilike(f'%{search}%')
            )
        )
    
    if date_from:
        query = query.filter(Invoice.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
    
    if date_to:
        query = query.filter(Invoice.created_at <= datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1))
    
    invoices = query.order_by(Invoice.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('invoices.html', invoices=invoices, search=search, date_from=date_from, date_to=date_to)

@app.route('/invoices/<int:id>')
@login_required
def view_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    return render_template('view_invoice.html', invoice=invoice)

@app.route('/invoices/<int:id>/pdf')
@login_required
def download_invoice_pdf(id):
    invoice = Invoice.query.get_or_404(id)
    pdf_buffer = generate_invoice_pdf(invoice)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f'{invoice.invoice_number}.pdf',
        mimetype='application/pdf'
    )

@app.route('/inventory')
@login_required
def inventory():
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')
    
    query = Product.query.filter_by(is_active=True)
    
    if filter_type == 'low_stock':
        query = query.filter(Product.quantity <= Config.LOW_STOCK_THRESHOLD)
    elif filter_type == 'out_of_stock':
        query = query.filter(Product.quantity == 0)
    
    products = query.order_by(Product.quantity.asc()).paginate(page=page, per_page=20)
    
    total_stock_value = db.session.query(
        db.func.sum(Product.quantity * Product.price)
    ).filter(Product.is_active == True).scalar() or 0
    
    total_cost_value = db.session.query(
        db.func.sum(Product.quantity * Product.cost_price)
    ).filter(Product.is_active == True).scalar() or 0
    
    return render_template('inventory.html', 
        products=products, 
        filter_type=filter_type,
        total_stock_value=float(total_stock_value),
        total_cost_value=float(total_cost_value)
    )

@app.route('/inventory/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_stock(id):
    product = Product.query.get_or_404(id)
    adjustment = int(request.form.get('adjustment', 0))
    
    product.quantity += adjustment
    if product.quantity < 0:
        product.quantity = 0
    
    db.session.commit()
    
    log_activity(current_user.id, 'STOCK_UPDATE', f'Updated stock for {product.name}: {adjustment:+d}', request.remote_addr)
    flash('Stock updated successfully!', 'success')
    return redirect(url_for('inventory'))

@app.route('/reports')
@login_required
@admin_required
def reports():
    return render_template('reports.html')

@app.route('/activity-logs')
@login_required
@admin_required
def activity_logs():
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('activity_logs.html', logs=logs)

@app.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.username).all()
    return render_template('users.html', users=all_users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'cashier')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return redirect(url_for('add_user'))
        
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        log_activity(current_user.id, 'USER_ADD', f'Added user: {username}', request.remote_addr)
        flash('User added successfully!', 'success')
        return redirect(url_for('users'))
    
    return render_template('add_user.html')

@app.route('/api/products', methods=['GET'])
@login_required
def api_products():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/products/search', methods=['GET'])
@login_required
def api_search_products():
    query = request.args.get('q', '')
    products = Product.query.filter(
        Product.is_active == True,
        db.or_(
            Product.name.ilike(f'%{query}%'),
            Product.barcode.ilike(f'%{query}%')
        )
    ).limit(20).all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/customers', methods=['GET'])
@login_required
def api_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])

@app.route('/api/customers/search', methods=['GET'])
@login_required
def api_search_customers():
    query = request.args.get('q', '')
    customers = Customer.query.filter(
        db.or_(
            Customer.name.ilike(f'%{query}%'),
            Customer.mobile.ilike(f'%{query}%')
        )
    ).limit(10).all()
    return jsonify([c.to_dict() for c in customers])

@app.route('/api/invoice/create', methods=['POST'])
@login_required
def api_create_invoice():
    data = request.get_json()
    
    try:
        customer_id = data.get('customer_id')
        items = data.get('items', [])
        discount_percent = Decimal(str(data.get('discount_percent', 0)))
        payment_method = data.get('payment_method', 'cash')
        notes = data.get('notes', '')
        
        if not items:
            return jsonify({'error': 'No items in cart'}), 400
        
        subtotal = Decimal('0')
        invoice_items = []
        
        for item in items:
            product = Product.query.get(item['product_id'])
            if not product:
                return jsonify({'error': f'Product not found: {item["product_id"]}'}), 400
            
            if product.quantity < item['quantity']:
                return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
            
            item_total = product.price * item['quantity']
            subtotal += item_total
            
            invoice_items.append({
                'product': product,
                'quantity': item['quantity'],
                'unit_price': product.price,
                'total_price': item_total
            })
        
        tax_rate = Decimal(str(Config.TAX_RATE * 100))
        tax_amount = subtotal * Decimal(str(Config.TAX_RATE))
        discount_amount = subtotal * (discount_percent / Decimal('100'))
        total_amount = subtotal + tax_amount - discount_amount
        
        invoice = Invoice(
            invoice_number=Invoice.generate_invoice_number(),
            customer_id=customer_id,
            created_by=current_user.id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            tax_rate=tax_rate,
            discount_amount=discount_amount,
            discount_percent=discount_percent,
            total_amount=total_amount,
            payment_method=payment_method,
            notes=notes
        )
        
        db.session.add(invoice)
        db.session.flush()
        
        for item_data in invoice_items:
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item_data['product'].id,
                product_name=item_data['product'].name,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            db.session.add(invoice_item)
            
            item_data['product'].quantity -= item_data['quantity']
        
        if customer_id:
            customer = Customer.query.get(customer_id)
            if customer:
                customer.total_purchases += total_amount
                customer.loyalty_points += int(total_amount / 100)
        
        db.session.commit()
        
        log_activity(current_user.id, 'INVOICE_CREATE', 
            f'Created invoice: {invoice.invoice_number}, Total: {total_amount}', 
            request.remote_addr)
        
        return jsonify({
            'success': True,
            'invoice': invoice.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/invoice/<int:id>', methods=['GET'])
@login_required
def api_get_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    return jsonify(invoice.to_dict())

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def api_dashboard_stats():
    today = datetime.utcnow().date()
    
    daily_sales = []
    for i in range(7):
        date = today - timedelta(days=i)
        sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
            db.func.date(Invoice.created_at) == date
        ).scalar() or 0
        daily_sales.append({
            'date': date.strftime('%Y-%m-%d'),
            'day': date.strftime('%a'),
            'sales': float(sales)
        })
    daily_sales.reverse()
    
    monthly_sales = []
    for i in range(6):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        sales = db.session.query(db.func.sum(Invoice.total_amount)).filter(
            Invoice.created_at >= month_start,
            Invoice.created_at <= month_end
        ).scalar() or 0
        monthly_sales.append({
            'month': month_start.strftime('%b %Y'),
            'sales': float(sales)
        })
    monthly_sales.reverse()
    
    top_products = db.session.query(
        Product.name,
        db.func.sum(InvoiceItem.quantity).label('total_qty')
    ).join(InvoiceItem).group_by(Product.id).order_by(
        db.desc('total_qty')
    ).limit(5).all()
    
    out_of_stock = Product.query.filter(
        Product.is_active == True,
        Product.quantity == 0
    ).count()
    
    low_stock = Product.query.filter(
        Product.is_active == True,
        Product.quantity > 0,
        Product.quantity <= Config.LOW_STOCK_THRESHOLD
    ).count()
    
    return jsonify({
        'daily_sales': daily_sales,
        'monthly_sales': monthly_sales,
        'top_products': [{'name': p[0], 'quantity': p[1]} for p in top_products],
        'out_of_stock': out_of_stock,
        'low_stock': low_stock
    })

@app.route('/api/reports/export', methods=['GET'])
@login_required
@admin_required
def export_report():
    report_type = request.args.get('type', 'sales')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    if report_type == 'sales':
        query = Invoice.query
        if date_from:
            query = query.filter(Invoice.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            query = query.filter(Invoice.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
        
        invoices = query.order_by(Invoice.created_at.desc()).all()
        
        writer.writerow(['Invoice Number', 'Date', 'Customer', 'Subtotal', 'Tax', 'Discount', 'Total', 'Payment Method'])
        for inv in invoices:
            writer.writerow([
                inv.invoice_number,
                inv.created_at.strftime('%Y-%m-%d %H:%M'),
                inv.customer.name if inv.customer else 'Walk-in',
                float(inv.subtotal),
                float(inv.tax_amount),
                float(inv.discount_amount),
                float(inv.total_amount),
                inv.payment_method
            ])
    
    elif report_type == 'inventory':
        products = Product.query.filter_by(is_active=True).order_by(Product.name).all()
        
        writer.writerow(['Barcode', 'Name', 'Category', 'Price', 'Cost Price', 'Quantity', 'Stock Value'])
        for p in products:
            writer.writerow([
                p.barcode,
                p.name,
                p.category.name if p.category else '',
                float(p.price),
                float(p.cost_price),
                p.quantity,
                float(p.price * p.quantity)
            ])
    
    elif report_type == 'customers':
        customers = Customer.query.order_by(Customer.name).all()
        
        writer.writerow(['Name', 'Mobile', 'Email', 'Total Purchases', 'Loyalty Points', 'Invoice Count'])
        for c in customers:
            writer.writerow([
                c.name,
                c.mobile,
                c.email or '',
                float(c.total_purchases),
                c.loyalty_points,
                c.invoices.count()
            ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        as_attachment=True,
        download_name=f'{report_type}_report_{datetime.now().strftime("%Y%m%d")}.csv',
        mimetype='text/csv'
    )

@app.context_processor
def utility_processor():
    return {
        'now': datetime.utcnow(),
        'config': Config
    }

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
