from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:deno0707@localhost/abz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:#Deno0707@69.197.187.23:5432/abz'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after db initialization
from models import Branch, Category, User, Product, OrderType, Order, OrderItem, StockTransaction

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    print("✅ All tables created successfully in PostgreSQL.")

@app.route("/")
def index():
    """Home page with featured products"""
    # Get products that are displayed to customers
    products = Product.query.filter_by(display=True).limit(8).all()
    categories = Category.query.all()
    return render_template('index.html', products=products, categories=categories)

@app.route("/products")
def products():
    """Product showcase page with search and filtering"""
    search = request.args.get('search', '')
    category_id = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    query = Product.query.filter_by(display=True)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    if category_id:
        query = query.filter_by(categoryid=category_id)
    
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()
    
    return render_template('products.html', products=products, categories=categories, search=search, category_id=category_id)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    """Individual product detail page"""
    product = Product.query.get_or_404(product_id)
    if not product.display:
        flash('Product not found', 'error')
        return redirect(url_for('products'))
    
    return render_template('product_detail.html', product=product)

@app.route("/login", methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email,
            firstname=firstname,
            lastname=lastname,
            password=hashed_password,
            role='customer'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route("/logout")
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route("/profile")
@login_required
def profile():
    """User profile page with order history"""
    orders = Order.query.filter_by(userid=current_user.id).order_by(Order.created_at.desc()).all()
    
    # Calculate totals for each order
    orders_with_totals = []
    for order in orders:
        total = 0
        for item in order.order_items:
            if item.product and item.product.sellingprice:
                total += item.product.sellingprice * item.quantity
        orders_with_totals.append({
            'order': order,
            'total': total
        })
    
    return render_template('profile.html', orders_with_totals=orders_with_totals)

@app.route("/order/<int:order_id>")
@login_required
def order_detail(order_id):
    """Individual order detail page"""
    order = Order.query.get_or_404(order_id)
    
    # Ensure user can only view their own orders
    if order.userid != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('profile'))
    
    # Calculate total from order items
    total = 0
    for item in order.order_items:
        if item.product and item.product.sellingprice:
            total += item.product.sellingprice * item.quantity
    
    return render_template('order_detail.html', order=order, total=total)

@app.route("/add_to_cart", methods=['POST'])
def add_to_cart():
    """Add product to cart (session-based)"""
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    product = Product.query.get_or_404(product_id)
    if not product.display:
        return jsonify({'success': False, 'message': 'Product not available'})
    
    if 'cart' not in session:
        session['cart'] = {}
    
    if str(product_id) in session['cart']:
        session['cart'][str(product_id)] += quantity
    else:
        session['cart'][str(product_id)] = quantity
    
    session.modified = True
    return jsonify({'success': True, 'message': 'Added to cart', 'cart_count': len(session['cart'])})

@app.route("/cart")
def cart():
    """Shopping cart page"""
    cart_items = []
    total = 0
    
    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(product_id)
            if product and product.display:
                item_total = product.sellingprice * quantity if product.sellingprice else 0
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route("/update_cart", methods=['POST'])
def update_cart():
    """Update cart quantities"""
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 0))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    if quantity <= 0:
        session['cart'].pop(str(product_id), None)
    else:
        session['cart'][str(product_id)] = quantity
    
    session.modified = True
    return redirect(url_for('cart'))

@app.route("/checkout", methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page and order processing"""
    if request.method == 'POST':
        # Get order type (assuming walk-in for now)
        order_type = OrderType.query.filter_by(name='Walk-in').first()
        if not order_type:
            # Create walk-in order type if it doesn't exist
            order_type = OrderType(name='Walk-in')
            db.session.add(order_type)
            db.session.commit()
        
        # Create order
        order = Order(
            userid=current_user.id,
            ordertypeid=order_type.id,
            branchid=1,  # Default branch, you might want to make this dynamic
            approvalstatus=False
        )
        db.session.add(order)
        db.session.commit()
        
        # Add order items
        total = 0
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(product_id)
            if product and product.display:
                order_item = OrderItem(
                    orderid=order.id,
                    productid=product.id,
                    quantity=quantity
                )
                db.session.add(order_item)
                total += (product.sellingprice or 0) * quantity
        
        db.session.commit()
        
        # Clear cart
        session.pop('cart', None)
        
        flash(f'Order placed successfully! Order ID: {order.id}', 'success')
        return redirect(url_for('order_detail', order_id=order.id))
    
    # GET request - show checkout page
    cart_items = []
    total = 0
    
    if 'cart' in session:
        for product_id, quantity in session['cart'].items():
            product = Product.query.get(product_id)
            if product and product.display:
                item_total = product.sellingprice * quantity if product.sellingprice else 0
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total': item_total
                })
                total += item_total
    
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route("/api/search_products")
def api_search_products():
    """API endpoint for product search"""
    search = request.args.get('q', '')
    products = Product.query.filter(
        Product.display == True,
        Product.name.ilike(f'%{search}%')
    ).limit(10).all()
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'price': product.sellingprice,
            'image_url': product.image_url,
            'category': product.category.name if product.category else ''
        })
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
