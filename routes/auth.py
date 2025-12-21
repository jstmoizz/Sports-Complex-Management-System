from flask import Blueprint, render_template, request, redirect, session, flash
from main.db import get_connection
import hashlib
import re

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/', methods=['GET'])
def home():
    return redirect('/login')


@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            cms_id = request.form.get('cms_id', '').strip()
            password = request.form.get('password', '')

            # Validation
            if not name or not email or not cms_id or not password:
                error = "All fields are required."
                return render_template('register.html', error=error)
            
            if len(name) < 3:
                error = "Full name must be at least 3 characters long."
                return render_template('register.html', error=error)
            
            if not is_valid_email(email):
                error = "Please enter a valid email address."
                return render_template('register.html', error=error)
            
            # CMS ID Validation - must be exactly 6 digits
            if not cms_id.isdigit():
                error = "CMS ID must contain only digits."
                return render_template('register.html', error=error, cms_id=cms_id)
            
            if len(cms_id) != 6:
                error = "CMS ID must be exactly 6 digits long."
                return render_template('register.html', error=error, cms_id=cms_id)
            
            if len(password) < 6:
                error = "Password must be at least 6 characters long."
                return render_template('register.html', error=error)

            password_hash = hashlib.sha256(password.encode()).hexdigest()

            conn = get_connection()
            cur = conn.cursor()

            try:
                cur.execute("""
                    INSERT INTO users (full_name, email, cms_id, password, membership_status)
                    VALUES (%s, %s, %s, %s, 'inactive')
                """, (name, email, cms_id, password_hash))

                conn.commit()
                conn.close()
                
                flash_message = "Account created successfully! Please login to continue."
                return redirect(f'/login?message={flash_message}')
            
            except Exception as db_error:
                conn.close()
                if 'Duplicate entry' in str(db_error):
                    if 'email' in str(db_error).lower():
                        error = "This email address is already registered. Please login or use a different email."
                    elif 'cms_id' in str(db_error).lower():
                        error = "This CMS ID is already registered. Please use a different CMS ID."
                    else:
                        error = "This account already exists. Please try again."
                else:
                    error = "An error occurred during registration. Please try again."
                return render_template('register.html', error=error, cms_id=cms_id)

        except Exception as e:
            error = "An unexpected error occurred. Please try again."
            return render_template('register.html', error=error)

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET','POST'])
def login():
    error = request.args.get('error', '')
    message = request.args.get('message', '')
    
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')

            # Validation
            if not email or not password:
                error = "Please enter both email and password."
                return render_template('login.html', error=error)

            if not is_valid_email(email):
                error = "Please enter a valid email address."
                return render_template('login.html', error=error)

            conn = get_connection()
            cur = conn.cursor()

            password_hash = hashlib.sha256(password.encode()).hexdigest()

            cur.execute("""
                SELECT * FROM users
                WHERE email=%s AND password=%s
            """, (email, password_hash))

            user = cur.fetchone()
            conn.close()

            if user:
                session['user_id'] = user['id']
                session['role'] = user['role']
                return redirect('/admin' if user['role']=='admin' else '/user')
            else:
                # Check if email exists but wrong password
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE email=%s", (email,))
                email_exists = cur.fetchone()
                conn.close()

                if email_exists:
                    error = "Incorrect password. Please try again or reset your password."
                else:
                    error = "Account not found. Please check your email or register to create a new account."
                
                return render_template('login.html', error=error)

        except Exception as e:
            error = "An error occurred during login. Please try again."
            return render_template('login.html', error=error)

    return render_template('login.html', error=error, message=message)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
