from flask import Blueprint, render_template, session, redirect, request
from main.db import get_connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Get all users (excluding other admins) with their payment info and medical conditions
        cur.execute("""
            SELECT u.id, u.full_name, u.email, u.cms_id, u.membership_status, u.membership_end, u.medical_conditions
            FROM users u
            WHERE u.role = 'user'
            ORDER BY u.id DESC
        """)

        users = cur.fetchall()

        # Get unique facility transactions with correct payment details
        cur.execute("""
            SELECT p.id, p.transaction_id, p.user_id, u.full_name, u.cms_id,
                   p.amount, p.payment_date
            FROM payments p
            JOIN users u ON p.user_id = u.id
            WHERE p.payment_type = 'facility' AND u.role = 'user'
            ORDER BY p.payment_date DESC
        """)

        transactions = cur.fetchall()
        
        # Get all facilities
        cur.execute("SELECT id, name, monthly_fee, is_active FROM facilities ORDER BY id")
        facilities = cur.fetchall()
        
        # Get all ground bookings
        cur.execute("""
            SELECT gb.id, gb.user_id, u.full_name, u.cms_id, g.name AS ground_name,
                   gb.booking_date, gb.booking_time, gb.created_at
            FROM ground_bookings gb
            JOIN users u ON gb.user_id = u.id
            JOIN grounds g ON gb.ground_id = g.id
            ORDER BY gb.booking_date DESC, gb.booking_time DESC
        """)

        bookings = cur.fetchall()
        
        # Get user facility access details
        cur.execute("""
            SELECT uf.id, uf.user_id, u.full_name, u.cms_id, f.id AS facility_id, f.name AS facility_name,
                   uf.start_date, uf.last_payment_date
            FROM user_facilities uf
            JOIN users u ON uf.user_id = u.id
            JOIN facilities f ON uf.facility_id = f.id
            ORDER BY u.full_name, f.name
        """)

        user_facilities = cur.fetchall()
        
        conn.close()

        return render_template('admin_dashboard.html', users=users, transactions=transactions, facilities=facilities, bookings=bookings, user_facilities=user_facilities)
    
    except Exception as e:
        return render_template('error.html',
                             error='Database Error',
                             message='An error occurred while loading the admin dashboard. Please try again.')


@admin_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Delete all related data first (payments, user_facilities)
        cur.execute("DELETE FROM payments WHERE user_id=%s", (user_id,))
        cur.execute("DELETE FROM user_facilities WHERE user_id=%s", (user_id,))
        
        # Delete the user
        cur.execute("DELETE FROM users WHERE id=%s AND role='user'", (user_id,))

        conn.commit()
        conn.close()

        return redirect('/admin')
    
    except Exception as e:
        return render_template('error.html',
                             error='Error Deleting User',
                             message='An error occurred while deleting the user. Please try again.')


@admin_bp.route('/admin/add_facility', methods=['POST'])
def add_facility():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    try:
        facility_name = request.form.get('facility_name', '').strip()
        monthly_fee = request.form.get('monthly_fee', '1000').strip()

        if not facility_name:
            return redirect('/admin')

        # Validate and convert monthly fee
        try:
            fee = int(monthly_fee)
        except ValueError:
            fee = 1000

        conn = get_connection()
        cur = conn.cursor()

        # Add new facility
        cur.execute("""
            INSERT INTO facilities (name, monthly_fee, is_active)
            VALUES (%s, %s, 1)
        """, (facility_name, fee))

        conn.commit()
        conn.close()

        return redirect('/admin')

    except Exception as e:
        return redirect('/admin')


@admin_bp.route('/admin/delete_facility/<int:facility_id>', methods=['POST'])
def delete_facility(facility_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Delete facility (will cascade due to foreign key)
        cur.execute("DELETE FROM facilities WHERE id=%s", (facility_id,))

        conn.commit()
        conn.close()

        return redirect('/admin')

    except Exception as e:
        return redirect('/admin')


@admin_bp.route('/admin/revoke_facility/<int:user_facility_id>', methods=['POST'])
def revoke_facility(user_facility_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/login')

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Get the user and facility info before deleting
        cur.execute("""
            SELECT uf.user_id, f.name
            FROM user_facilities uf
            JOIN facilities f ON uf.facility_id = f.id
            WHERE uf.id=%s
        """, (user_facility_id,))

        facility_info = cur.fetchone()
        
        # Delete the user facility access
        cur.execute("DELETE FROM user_facilities WHERE id=%s", (user_facility_id,))

        conn.commit()
        conn.close()

        return redirect('/admin')

    except Exception as e:
        return redirect('/admin')
