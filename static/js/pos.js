let cart = [];
const TAX_RATE = 0.18;

document.addEventListener('DOMContentLoaded', function() {
    const productSearch = document.getElementById('productSearch');
    const clearCartBtn = document.getElementById('clearCart');
    const checkoutBtn = document.getElementById('checkoutBtn');
    const discountInput = document.getElementById('discountPercent');
    const categoryFilters = document.querySelectorAll('.category-filter');
    
    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('click', function() {
            const product = JSON.parse(this.dataset.product);
            addToCart(product);
        });
    });
    
    if (productSearch) {
        productSearch.addEventListener('input', debounce(function() {
            const query = this.value.toLowerCase();
            filterProducts(query);
        }, 300));
        
        productSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = this.value.trim();
                if (query) {
                    searchAndAddProduct(query);
                }
            }
        });
    }
    
    categoryFilters.forEach(btn => {
        btn.addEventListener('click', function() {
            categoryFilters.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const category = this.dataset.category;
            filterByCategory(category);
        });
    });
    
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', clearCart);
    }
    
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', processCheckout);
    }
    
    if (discountInput) {
        discountInput.addEventListener('input', updateTotals);
    }
});

function addToCart(product) {
    if (product.quantity <= 0) {
        showToast('Product is out of stock!', 'error');
        return;
    }
    
    const existingItem = cart.find(item => item.product_id === product.id);
    
    if (existingItem) {
        if (existingItem.quantity >= product.quantity) {
            showToast('Cannot add more than available stock!', 'error');
            return;
        }
        existingItem.quantity++;
    } else {
        cart.push({
            product_id: product.id,
            name: product.name,
            price: product.price,
            quantity: 1,
            max_quantity: product.quantity
        });
    }
    
    renderCart();
    updateTotals();
    showToast(`${product.name} added to cart`, 'success');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.product_id !== productId);
    renderCart();
    updateTotals();
}

function updateQuantity(productId, change) {
    const item = cart.find(item => item.product_id === productId);
    if (!item) return;
    
    const newQuantity = item.quantity + change;
    
    if (newQuantity <= 0) {
        removeFromCart(productId);
        return;
    }
    
    if (newQuantity > item.max_quantity) {
        showToast('Cannot exceed available stock!', 'error');
        return;
    }
    
    item.quantity = newQuantity;
    renderCart();
    updateTotals();
}

function renderCart() {
    const cartContainer = document.getElementById('cartItems');
    const emptyCart = document.getElementById('emptyCart');
    
    if (cart.length === 0) {
        cartContainer.innerHTML = `
            <div class="text-center text-muted py-5" id="emptyCart">
                <i class="bi bi-cart-x display-4"></i>
                <p class="mt-2">Cart is empty</p>
                <small>Click on products to add them</small>
            </div>
        `;
        document.getElementById('checkoutBtn').disabled = true;
        return;
    }
    
    document.getElementById('checkoutBtn').disabled = false;
    
    let html = '';
    cart.forEach(item => {
        html += `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">Rs. ${item.price.toLocaleString('en-PK', {minimumFractionDigits: 2})} each</div>
                </div>
                <div class="cart-item-qty">
                    <button class="btn btn-sm btn-outline-secondary" onclick="updateQuantity(${item.product_id}, -1)">
                        <i class="bi bi-dash"></i>
                    </button>
                    <span>${item.quantity}</span>
                    <button class="btn btn-sm btn-outline-secondary" onclick="updateQuantity(${item.product_id}, 1)">
                        <i class="bi bi-plus"></i>
                    </button>
                </div>
                <div class="cart-item-total">Rs. ${(item.price * item.quantity).toLocaleString('en-PK', {minimumFractionDigits: 2})}</div>
                <button class="btn btn-sm btn-outline-danger cart-item-remove" onclick="removeFromCart(${item.product_id})">
                    <i class="bi bi-x"></i>
                </button>
            </div>
        `;
    });
    
    cartContainer.innerHTML = html;
}

function updateTotals() {
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const discountPercent = parseFloat(document.getElementById('discountPercent').value) || 0;
    const taxAmount = subtotal * TAX_RATE;
    const discountAmount = subtotal * (discountPercent / 100);
    const total = subtotal + taxAmount - discountAmount;
    
    document.getElementById('subtotal').textContent = 'Rs. ' + subtotal.toLocaleString('en-PK', {minimumFractionDigits: 2});
    document.getElementById('taxAmount').textContent = 'Rs. ' + taxAmount.toLocaleString('en-PK', {minimumFractionDigits: 2});
    document.getElementById('discountAmount').textContent = '-Rs. ' + discountAmount.toLocaleString('en-PK', {minimumFractionDigits: 2});
    document.getElementById('totalAmount').textContent = 'Rs. ' + total.toLocaleString('en-PK', {minimumFractionDigits: 2});
}

function clearCart() {
    if (cart.length === 0) return;
    
    if (confirm('Are you sure you want to clear the cart?')) {
        cart = [];
        renderCart();
        updateTotals();
    }
}

async function processCheckout() {
    if (cart.length === 0) {
        showToast('Cart is empty!', 'error');
        return;
    }
    
    const customerId = document.getElementById('customerSelect').value || null;
    const discountPercent = parseFloat(document.getElementById('discountPercent').value) || 0;
    const paymentMethod = document.getElementById('paymentMethod').value;
    
    const checkoutBtn = document.getElementById('checkoutBtn');
    checkoutBtn.disabled = true;
    checkoutBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';
    
    try {
        const response = await fetch('/api/invoice/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                customer_id: customerId,
                items: cart.map(item => ({
                    product_id: item.product_id,
                    quantity: item.quantity
                })),
                discount_percent: discountPercent,
                payment_method: paymentMethod
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            checkoutBtn.disabled = false;
            checkoutBtn.innerHTML = '<i class="bi bi-check-circle"></i> Complete Sale';
            return;
        }
        
        showInvoiceModal(data.invoice);
        
        cart = [];
        renderCart();
        updateTotals();
        document.getElementById('discountPercent').value = 0;
        document.getElementById('customerSelect').value = '';
        
        checkoutBtn.disabled = false;
        checkoutBtn.innerHTML = '<i class="bi bi-check-circle"></i> Complete Sale';
        
    } catch (error) {
        console.error('Checkout error:', error);
        showToast('An error occurred. Please try again.', 'error');
        checkoutBtn.disabled = false;
        checkoutBtn.innerHTML = '<i class="bi bi-check-circle"></i> Complete Sale';
    }
}

function showInvoiceModal(invoice) {
    const modal = new bootstrap.Modal(document.getElementById('invoiceModal'));
    const content = document.getElementById('invoiceContent');
    
    let itemsHtml = '';
    invoice.items.forEach((item, index) => {
        itemsHtml += `
            <tr>
                <td>${index + 1}</td>
                <td>${item.product_name}</td>
                <td class="text-center">${item.quantity}</td>
                <td class="text-end">Rs. ${item.unit_price.toLocaleString('en-PK', {minimumFractionDigits: 2})}</td>
                <td class="text-end">Rs. ${item.total_price.toLocaleString('en-PK', {minimumFractionDigits: 2})}</td>
            </tr>
        `;
    });
    
    content.innerHTML = `
        <div class="text-center mb-4">
            <h4 class="text-primary">Grocery Store</h4>
            <p class="text-muted mb-0">Invoice: ${invoice.invoice_number}</p>
            <p class="text-muted">${new Date(invoice.created_at).toLocaleString()}</p>
        </div>
        
        <div class="row mb-3">
            <div class="col-6">
                <strong>Customer:</strong><br>
                ${invoice.customer_name}<br>
                ${invoice.customer_mobile || ''}
            </div>
            <div class="col-6 text-end">
                <strong>Payment:</strong><br>
                ${invoice.payment_method.toUpperCase()}
            </div>
        </div>
        
        <table class="table table-sm table-bordered">
            <thead class="table-light">
                <tr>
                    <th>#</th>
                    <th>Product</th>
                    <th class="text-center">Qty</th>
                    <th class="text-end">Price</th>
                    <th class="text-end">Total</th>
                </tr>
            </thead>
            <tbody>
                ${itemsHtml}
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="4" class="text-end"><strong>Subtotal:</strong></td>
                    <td class="text-end">Rs. ${invoice.subtotal.toLocaleString('en-PK', {minimumFractionDigits: 2})}</td>
                </tr>
                <tr>
                    <td colspan="4" class="text-end"><strong>Tax (${invoice.tax_rate}%):</strong></td>
                    <td class="text-end">Rs. ${invoice.tax_amount.toLocaleString('en-PK', {minimumFractionDigits: 2})}</td>
                </tr>
                ${invoice.discount_amount > 0 ? `
                <tr>
                    <td colspan="4" class="text-end"><strong>Discount (${invoice.discount_percent}%):</strong></td>
                    <td class="text-end text-danger">-Rs. ${invoice.discount_amount.toLocaleString('en-PK', {minimumFractionDigits: 2})}</td>
                </tr>
                ` : ''}
                <tr class="table-primary">
                    <td colspan="4" class="text-end"><strong class="fs-5">Total:</strong></td>
                    <td class="text-end"><strong class="fs-5">Rs. ${invoice.total_amount.toLocaleString('en-PK', {minimumFractionDigits: 2})}</strong></td>
                </tr>
            </tfoot>
        </table>
        
        <div class="text-center text-muted">
            <small>Thank you for shopping with us!</small>
        </div>
    `;
    
    document.getElementById('downloadPdfBtn').href = `/invoices/${invoice.id}/pdf`;
    
    document.getElementById('printInvoiceBtn').onclick = function() {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Invoice ${invoice.invoice_number}</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body { padding: 20px; }
                    @media print { body { padding: 0; } }
                </style>
            </head>
            <body>
                ${content.innerHTML}
                <script>window.onload = function() { window.print(); }</script>
            </body>
            </html>
        `);
        printWindow.document.close();
    };
    
    modal.show();
}

function filterProducts(query) {
    document.querySelectorAll('.product-item').forEach(item => {
        const card = item.querySelector('.product-card');
        const product = JSON.parse(card.dataset.product);
        const matches = product.name.toLowerCase().includes(query) || 
                       product.barcode.toLowerCase().includes(query);
        item.style.display = matches ? '' : 'none';
    });
}

function filterByCategory(category) {
    document.querySelectorAll('.product-item').forEach(item => {
        if (category === 'all') {
            item.style.display = '';
        } else {
            const itemCategory = item.dataset.category;
            item.style.display = itemCategory === category ? '' : 'none';
        }
    });
}

async function searchAndAddProduct(query) {
    try {
        const response = await fetch(`/api/products/search?q=${encodeURIComponent(query)}`);
        const products = await response.json();
        
        if (products.length === 1) {
            addToCart(products[0]);
            document.getElementById('productSearch').value = '';
        } else if (products.length > 1) {
            filterProducts(query);
        } else {
            showToast('Product not found', 'error');
        }
    } catch (error) {
        console.error('Search error:', error);
    }
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function showToast(message, type = 'success') {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1100';
        document.body.appendChild(toastContainer);
    }
    
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'error' ? 'bg-danger' : type === 'warning' ? 'bg-warning' : 'bg-success';
    
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass}" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}
