from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db
import requests
import os
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yvkjkelcjklcl'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:deno0707@localhost/abz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:#Deno0707@69.197.187.23:5432/abz'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Brevo API configuration
app.config['BREVO_API_KEY'] = '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'  # Replace with your Brevo API key
app.config['BREVO_SENDER_EMAIL'] = 'admin@abzhardware.co.ke'  # Replace with your sender email
app.config['BREVO_SENDER_NAME'] = 'ABZ Hardware'  # Replace with your sender name

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after db initialization
from models import Branch, Category, User, Product, OrderType, Order, OrderItem, StockTransaction, PasswordReset

def send_welcome_email(user):
    """Send welcome email to newly registered user using Brevo API"""
    api_key = app.config['BREVO_API_KEY']
    sender_email = app.config['BREVO_SENDER_EMAIL']
    sender_name = app.config['BREVO_SENDER_NAME']
    url = 'https://api.brevo.com/v3/smtp/email'
    headers = {
        'accept': 'application/json',
        'api-key': api_key,
        'content-type': 'application/json',
    }
    data = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": user.email, "name": f"{user.firstname} {user.lastname}"}],
        "subject": "Welcome to ABZ Hardware! 🛠️",
        "htmlContent": f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to ABZ Hardware</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 700;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .welcome-section {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .welcome-section h2 {{
                    color: #2c3e50;
                    margin-bottom: 15px;
                    font-size: 24px;
                }}
                .account-details {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #ffd700;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 5px;
                }}
                .account-details h3 {{
                    color: #2c3e50;
                    margin-top: 0;
                    font-size: 18px;
                }}
                .account-details p {{
                    margin: 8px 0;
                    color: #555;
                }}
                .features {{
                    margin: 30px 0;
                }}
                .features h3 {{
                    color: #2c3e50;
                    margin-bottom: 15px;
                    font-size: 18px;
                }}
                .feature-list {{
                    list-style: none;
                    padding: 0;
                }}
                .feature-list li {{
                    padding: 10px 0;
                    border-bottom: 1px solid #eee;
                    position: relative;
                    padding-left: 30px;
                }}
                .feature-list li:before {{
                    content: "✓";
                    position: absolute;
                    left: 0;
                    color: #27ae60;
                    font-weight: bold;
                    font-size: 16px;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(45deg, #ffd700, #ffed4e);
                    color: #1a1a1a;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 50px;
                    font-weight: 600;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
                    transition: all 0.3s ease;
                }}
                .cta-button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
                }}
                .footer {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .footer h4 {{
                    margin: 0 0 15px 0;
                    color: #ffd700;
                }}
                .footer p {{
                    margin: 5px 0;
                    font-size: 14px;
                    opacity: 0.8;
                }}
                .social-links {{
                    margin: 20px 0;
                }}
                .social-links a {{
                    color: #ffd700;
                    text-decoration: none;
                    margin: 0 10px;
                    font-weight: 600;
                }}
                .disclaimer {{
                    font-size: 12px;
                    opacity: 0.6;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #444;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛠️ ABZ Hardware</h1>
                    <p>Your Trusted Partner for Quality Tools & Equipment</p>
                </div>
                
                <div class="content">
                    <div class="welcome-section">
                        <h2>Welcome to the Family! 🎉</h2>
                        <p>Dear <strong>{user.firstname} {user.lastname}</strong>,</p>
                        <p>We're thrilled to welcome you to ABZ Hardware! Your account has been successfully created and you're now part of our growing community of professionals and DIY enthusiasts.</p>
                    </div>
                    
                    <div class="account-details">
                        <h3>📋 Your Account Details</h3>
                        <p><strong>Email:</strong> {user.email}</p>
                        <p><strong>Name:</strong> {user.firstname} {user.lastname}</p>
                        <p><strong>Member Since:</strong> {user.created_at.strftime('%B %d, %Y')}</p>
                        <p><strong>Account Type:</strong> Customer</p>
                    </div>
                    
                    <div class="features">
                        <h3>🚀 What You Can Do Now</h3>
                        <ul class="feature-list">
                            <li>Browse our extensive catalog of professional tools and equipment</li>
                            <li>Place orders for quality hardware with secure checkout</li>
                            <li>Track your order history and delivery status</li>
                            <li>Update your profile and manage account settings</li>
                            <li>Access exclusive customer support and expert advice</li>
                            <li>Receive notifications about new products and special offers</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 40px 0;">
                        <a href="https://abzhardware.co.ke" class="cta-button">
                            🛒 Start Shopping Now
                        </a>
                    </div>
                    
                 
                </div>
                
                <div class="footer">
                    <h4>ABZ Hardware</h4>
                    <p>Your trusted partner for premium tools and equipment</p>
                    <div class="social-links">
                        <a href="#">📧 Email Support</a> |
                        <a href="#">📞 Phone Support</a> |
                        <a href="#">🌐 Website</a>
                    </div>
                    <div class="disclaimer">
                        <p>This is an automated welcome message. Please do not reply to this email.</p>
                        <p>For support, visit our website or contact our customer service team.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"✅ Welcome email sent to {user.email}")
        else:
            print(f"❌ Failed to send welcome email to {user.email}: {response.text}")
    except Exception as e:
        print(f"❌ Exception sending welcome email to {user.email}: {str(e)}")

def send_password_reset_email(user, reset_token):
    """Send password reset email using Brevo API"""
    api_key = app.config['BREVO_API_KEY']
    sender_email = app.config['BREVO_SENDER_EMAIL']
    sender_name = app.config['BREVO_SENDER_NAME']
    url = 'https://api.brevo.com/v3/smtp/email'
    headers = {
        'accept': 'application/json',
        'api-key': api_key,
        'content-type': 'application/json',
    }
    
    reset_url = f"https://abzhardware.co.ke/reset-password/{reset_token}"
    
    # Debug: Print the request data
    print(f"🔍 Debug: Sending password reset email to {user.email}")
    print(f"🔍 Debug: API Key: {api_key[:20]}...")
    print(f"🔍 Debug: Sender Email: {sender_email}")
    print(f"🔍 Debug: Reset URL: {reset_url}")
    
    data = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": user.email, "name": f"{user.firstname} {user.lastname}"}],
        "subject": "Password Reset Request - ABZ Hardware 🔐",
        "htmlContent": f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset - ABZ Hardware</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 700;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .alert-box {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .reset-button {{
                    display: inline-block;
                    background: linear-gradient(45deg, #ffd700, #ffed4e);
                    color: #1a1a1a;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 50px;
                    font-weight: 600;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
                }}
                .code-box {{
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    text-align: center;
                    font-family: 'Courier New', monospace;
                    font-size: 18px;
                    font-weight: bold;
                    color: #495057;
                }}
                .footer {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .footer h4 {{
                    margin: 0 0 15px 0;
                    color: #ffd700;
                }}
                .disclaimer {{
                    font-size: 12px;
                    opacity: 0.6;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #444;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 ABZ Hardware</h1>
                    <p>Password Reset Request</p>
                </div>
                
                <div class="content">
                    <h2 style="color: #2c3e50; text-align: center;">Password Reset Request</h2>
                    
                    <p>Dear <strong>{user.firstname} {user.lastname}</strong>,</p>
                    
                    <p>We received a request to reset your password for your ABZ Hardware account. If you didn't make this request, you can safely ignore this email.</p>
                    
                    <div class="alert-box">
                        <h3 style="color: #856404; margin-top: 0;">⚠️ Security Notice</h3>
                        <p style="margin: 0;">This link will expire in 1 hour for your security.</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" class="reset-button">
                            🔑 Reset My Password
                        </a>
                    </div>
                    
                    <p><strong>Or copy this verification code:</strong></p>
                    <div class="code-box">
                        {reset_token[:8].upper()}
                    </div>
                    
                    <p><strong>What happens next?</strong></p>
                    <ul>
                        <li>Click the button above or use the verification code</li>
                        <li>You'll be taken to a secure page to set your new password</li>
                        <li>Your new password will be active immediately</li>
                        <li>You'll receive a confirmation email once the password is changed</li>
                    </ul>
                    
                    <p><strong>Need help?</strong> If you're having trouble, contact our support team.</p>
                </div>
                
                <div class="footer">
                    <h4>ABZ Hardware</h4>
                    <p>Your trusted partner for premium tools and equipment</p>
                    <div class="disclaimer">
                        <p>This is an automated security message. Please do not reply to this email.</p>
                        <p>If you didn't request this password reset, please contact us immediately.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    }
    try:
        print(f"🔍 Debug: Making API request to Brevo...")
        response = requests.post(url, headers=headers, json=data)
        print(f"🔍 Debug: Response status code: {response.status_code}")
        print(f"🔍 Debug: Response text: {response.text}")
        
        if response.status_code == 201:
            print(f"✅ Password reset email sent to {user.email}")
            return True
        else:
            print(f"❌ Failed to send password reset email to {user.email}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception sending password reset email to {user.email}: {str(e)}")
        return False

def send_password_change_alert(user):
    """Send password change confirmation email using Brevo API"""
    api_key = app.config['BREVO_API_KEY']
    sender_email = app.config['BREVO_SENDER_EMAIL']
    sender_name = app.config['BREVO_SENDER_NAME']
    url = 'https://api.brevo.com/v3/smtp/email'
    headers = {
        'accept': 'application/json',
        'api-key': api_key,
        'content-type': 'application/json',
    }
    
    data = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": user.email, "name": f"{user.firstname} {user.lastname}"}],
        "subject": "Password Changed Successfully - ABZ Hardware ✅",
        "htmlContent": f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Changed - ABZ Hardware</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 700;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .success-box {{
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .info-box {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #17a2b8;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 5px;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(45deg, #ffd700, #ffed4e);
                    color: #1a1a1a;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 50px;
                    font-weight: 600;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
                }}
                .footer {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .footer h4 {{
                    margin: 0 0 15px 0;
                    color: #ffd700;
                }}
                .disclaimer {{
                    font-size: 12px;
                    opacity: 0.6;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #444;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ ABZ Hardware</h1>
                    <p>Password Changed Successfully</p>
                </div>
                
                <div class="content">
                    <h2 style="color: #2c3e50; text-align: center;">Password Updated Successfully!</h2>
                    
                    <p>Dear <strong>{user.firstname} {user.lastname}</strong>,</p>
                    
                    <div class="success-box">
                        <h3 style="color: #155724; margin-top: 0;">🎉 Password Change Confirmed</h3>
                        <p style="margin: 0;">Your ABZ Hardware account password has been successfully updated.</p>
                    </div>
                    
                    <div class="info-box">
                        <h3 style="color: #2c3e50; margin-top: 0;">📋 Change Details</h3>
                        <p><strong>Account:</strong> {user.email}</p>
                        <p><strong>Changed At:</strong> {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}</p>
                        <p><strong>Status:</strong> ✅ Successfully Updated</p>
                    </div>
                    
                    <p><strong>What you should know:</strong></p>
                    <ul>
                        <li>Your new password is now active</li>
                        <li>You can log in with your new password immediately</li>
                        <li>All your account data and settings remain unchanged</li>
                        <li>If you didn't make this change, contact us immediately</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:5000/login" class="cta-button">
                            🔐 Login to Your Account
                        </a>
                    </div>
                    
                    <p><strong>Security Tips:</strong></p>
                    <ul>
                        <li>Use a strong, unique password</li>
                        <li>Never share your password with anyone</li>
                        <li>Log out from shared devices</li>
                        <li>Enable two-factor authentication if available</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <h4>ABZ Hardware</h4>
                    <p>Your trusted partner for premium tools and equipment</p>
                    <div class="disclaimer">
                        <p>This is an automated security notification. Please do not reply to this email.</p>
                        <p>If you didn't change your password, contact our support team immediately.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"✅ Password change alert sent to {user.email}")
            return True
        else:
            print(f"❌ Failed to send password change alert to {user.email}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception sending password change alert to {user.email}: {str(e)}")
        return False

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
            # Check if user has customer role
            if user.role != 'customer':
                flash('Access denied. Only customers can log in to this portal.', 'error')
                return render_template('login.html')
            
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
        
        # Check password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email address is already registered. Please use a different email or try logging in.', 'error')
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
        
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            if 'duplicate key value violates unique constraint "users_email_key"' in str(e):
                flash('This email address is already registered. Please use a different email or try logging in.', 'error')
            else:
                flash('Registration failed. Please try again or contact support if the problem persists.', 'error')
            return render_template('register.html')
        
        # Send welcome email
        send_welcome_email(new_user)
        
        flash('Registration successful! Welcome email sent. Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    # Clean up expired tokens first
    cleanup_expired_tokens()
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate a secure reset token
            reset_token = secrets.token_urlsafe(32)
            
            # Create expiry time (1 hour from now)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            # Store token in database
            reset_token_obj = PasswordReset(
                user_id=user.id,
                token=reset_token,
                expires_at=expires_at
            )
            db.session.add(reset_token_obj)
            db.session.commit()
            
            # Send password reset email
            email_sent = send_password_reset_email(user, reset_token)
            
            if email_sent:
                flash(f'Password reset email sent to {email}. Please check your inbox.', 'success')
                return redirect(url_for('login'))
            else:
                # If email failed, remove the token from database
                db.session.delete(reset_token_obj)
                db.session.commit()
                flash('Failed to send reset email. Please try again.', 'error')
                return render_template('forgot_password.html')
        else:
            flash('Email not found in our system', 'error')
    
    return render_template('forgot_password.html')

@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    """Reset password page"""
    # Find valid reset token in database
    reset_token_obj = PasswordReset.query.filter_by(token=token).first()
    
    if not reset_token_obj or not reset_token_obj.is_valid():
        if reset_token_obj:
            # Mark expired tokens as used
            reset_token_obj.used = True
            db.session.commit()
        flash('Invalid or expired reset token. Please request a new password reset.', 'error')
        return redirect(url_for('forgot_password'))
    
    user = User.query.get(reset_token_obj.user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('reset_password.html', token=token)
        
        # Update password
        user.password = generate_password_hash(password)
        
        # Mark token as used
        reset_token_obj.used = True
        
        db.session.commit()
        
        # Send password change alert email
        send_password_change_alert(user)
        
        flash('Password reset successfully! Please check your email for confirmation.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

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

@app.route("/change-password", methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate input
    if not current_password or not new_password or not confirm_password:
        flash('All password fields are required', 'error')
        return redirect(url_for('profile'))
    
    # Verify current password
    if not check_password_hash(current_user.password, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('profile'))
    
    # Check if new passwords match
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('profile'))
    
    # Check password length
    if len(new_password) < 6:
        flash('New password must be at least 6 characters long', 'error')
        return redirect(url_for('profile'))
    
    # Update password
    current_user.password = generate_password_hash(new_password)
    db.session.commit()
    
    # Send password change alert email
    print(f"🔍 Sending password change alert to {current_user.email}")
    email_sent = send_password_change_alert(current_user)
    
    if email_sent:
        flash('Password updated successfully! Please check your email for confirmation.', 'success')
    else:
        flash('Password updated successfully! Email notification could not be sent.', 'warning')
    
    return redirect(url_for('profile'))

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
        # Get order type (Online for customer portal)
        order_type = OrderType.query.filter_by(name='Online').first()
        if not order_type:
            # Create Online order type if it doesn't exist
            order_type = OrderType(name='Online')
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
                    quantity=quantity,
                    buying_price=product.buyingprice,  # Capture buying price at time of order
                    original_price=product.sellingprice,  # Capture original selling price
                    final_price=product.sellingprice  # Set final price to selling price initially
                )
                db.session.add(order_item)
                total += (product.sellingprice or 0) * quantity
        
        db.session.commit()
        
        # Clear cart
        session.pop('cart', None)
        
        flash(f'Online order placed successfully! Order ID: {order.id}', 'success')
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

def test_brevo_api():
    """Test Brevo API connection"""
    api_key = app.config['BREVO_API_KEY']
    sender_email = app.config['BREVO_SENDER_EMAIL']
    sender_name = app.config['BREVO_SENDER_NAME']
    url = 'https://api.brevo.com/v3/smtp/email'
    headers = {
        'accept': 'application/json',
        'api-key': api_key,
        'content-type': 'application/json',
    }
    
    data = {
        "sender": {"name": sender_name, "email": sender_email},
        "to": [{"email": "test@example.com", "name": "Test User"}],
        "subject": "Test Email - ABZ Hardware",
        "htmlContent": "<h1>Test Email</h1><p>This is a test email to verify Brevo API connection.</p>"
    }
    
    try:
        print(f"🔍 Testing Brevo API connection...")
        print(f"🔍 API Key: {api_key[:20]}...")
        print(f"🔍 Sender Email: {sender_email}")
        print(f"🔍 Sender Name: {sender_name}")
        
        response = requests.post(url, headers=headers, json=data)
        print(f"🔍 Response status code: {response.status_code}")
        print(f"🔍 Response text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Brevo API test successful!")
            return True
        else:
            print(f"❌ Brevo API test failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception during Brevo API test: {str(e)}")
        return False

@app.route("/test-email")
def test_email():
    """Test email functionality"""
    if test_brevo_api():
        return "Email API test successful! Check console for details."
    else:
        return "Email API test failed! Check console for details."

def cleanup_expired_tokens():
    """Remove expired password reset tokens from database"""
    try:
        expired_tokens = PasswordReset.query.filter(
            PasswordReset.expires_at < datetime.utcnow()
        ).all()
        
        for token in expired_tokens:
            db.session.delete(token)
        
        if expired_tokens:
            db.session.commit()
            print(f"🧹 Cleaned up {len(expired_tokens)} expired password reset tokens")
            
    except Exception as e:
        print(f"❌ Error cleaning up expired tokens: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
