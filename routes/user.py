from flask import Blueprint, render_template, session, redirect, request
from main.db import get_connection
from datetime import date, timedelta

user_bp = Blueprint('user', __name__)

def check_membership(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT MAX(last_payment_date) AS last_pay
        FROM user_facilities
        WHERE user_id=%s
    """, (user_id,))

    last_pay = cur.fetchone()['last_pay']

    if last_pay and (date.today() - last_pay).days > 180:
        cur.execute("""
            UPDATE users
            SET membership_status='cancelled'
            WHERE id=%s
        """, (user_id,))
        conn.commit()

    conn.close()


@user_bp.route('/user')
def user_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    try:
        user_id = session['user_id']
        check_membership(user_id)

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()

        if not user:
            conn.close()
            return redirect('/login')

        # Get available facilities (user hasn't paid for yet)
        available_facilities = []
        ongoing_facilities = []
        
        if user['membership_status'] == 'active':
            # Get all active facilities
            cur.execute("SELECT * FROM facilities WHERE is_active=1")
            all_facilities = cur.fetchall()
            
            # Get facilities user has already paid for
            cur.execute("SELECT facility_id FROM user_facilities WHERE user_id=%s", (user_id,))
            paid_facilities = cur.fetchall()
            paid_facility_ids = [f['facility_id'] for f in paid_facilities]
            
            # Separate into available and ongoing
            for facility in all_facilities:
                if facility['id'] in paid_facility_ids:
                    ongoing_facilities.append(facility)
                else:
                    available_facilities.append(facility)

        conn.close()

        return render_template(
            'user_dashboard.html',
            user=user,
            available_facilities=available_facilities,
            ongoing_facilities=ongoing_facilities
        )
    
    except Exception as e:
        return redirect('/login')



@user_bp.route('/pay_membership', methods=['GET', 'POST'])
def pay_membership():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'GET':
        return render_template('payment_confirmation.html', 
                             payment_type='membership',
                             amount=2000,
                             description='6-Month Membership Access')
    
    # Process payment
    transaction_id = request.form.get('transaction_id', '').strip()
    
    # Validation
    if not transaction_id:
        return render_template('payment_confirmation.html',
                             payment_type='membership',
                             amount=2000,
                             description='6-Month Membership Access',
                             error='Transaction ID is required.')
    
    user_id = session['user_id']
    start = date.today()
    end = start + timedelta(days=180)

    conn = get_connection()
    cur = conn.cursor()

    # Update membership status
    cur.execute("""
        UPDATE users
        SET membership_status='active',
            membership_start=%s,
            membership_end=%s
        WHERE id=%s
    """, (start, end, user_id))

    # Record payment with transaction ID
    cur.execute("""
        INSERT INTO payments (user_id, amount, payment_type, transaction_id)
        VALUES (%s, 2000, 'membership', %s)
    """, (user_id, transaction_id))

    conn.commit()
    conn.close()

    # Redirect to medical information form
    return redirect('/medical_info')




@user_bp.route('/pay_facility/<int:facility_id>', methods=['GET', 'POST'])
def pay_facility(facility_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    # Check if user has active membership
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT membership_status FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    
    if not user or user['membership_status'] != 'active':
        conn.close()
        return render_template('error.html',
                             error='Membership Required',
                             message='You need an active membership to access facilities. Please purchase a membership first.')
    
    # Get facility details
    cur.execute("SELECT name, monthly_fee FROM facilities WHERE id=%s", (facility_id,))
    facility = cur.fetchone()
    
    if not facility:
        conn.close()
        return render_template('error.html',
                             error='Facility Not Found',
                             message='The facility you are trying to access does not exist.')
    
    conn.close()
    
    if request.method == 'GET':
        return render_template('payment_confirmation.html',
                             payment_type='facility',
                             facility_id=facility_id,
                             facility_name=facility['name'],
                             amount=facility['monthly_fee'],
                             description=f'Access to {facility["name"]}')
    
    # Process facility payment
    transaction_id = request.form.get('transaction_id', '').strip()
    
    # Validation
    if not transaction_id:
        return render_template('payment_confirmation.html',
                             payment_type='facility',
                             facility_id=facility_id,
                             facility_name=facility['name'],
                             amount=facility['monthly_fee'],
                             description=f'Access to {facility["name"]}',
                             error='Transaction ID is required.')
    
    today = date.today()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO user_facilities
        (user_id, facility_id, start_date, last_payment_date)
        VALUES (%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE last_payment_date=%s
    """, (user_id, facility_id, today, today, today))

    cur.execute("""
        INSERT INTO payments (user_id, amount, payment_type, transaction_id)
        VALUES (%s,%s,'facility', %s)
    """, (user_id, facility['monthly_fee'], transaction_id))

    conn.commit()
    conn.close()

    return render_template('payment_verified.html',
                         transaction_id=transaction_id,
                         amount=facility['monthly_fee'],
                         payment_type='Facility Access')


@user_bp.route('/medical_info', methods=['GET', 'POST'])
def medical_info():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        return redirect('/login')
    
    if request.method == 'GET':
        conn.close()
        return render_template('medical_info.html', user=user)
    
    # Check if user clicked skip button
    skip = request.form.get('skip')
    if skip:
        conn.close()
        return redirect('/user')
    
    # Process medical information form
    has_conditions = request.form.get('has_conditions', 'no')
    medical_info_text = request.form.get('medical_info', '').strip()
    
    # If user said Yes but didn't provide information, use placeholder
    if has_conditions == 'yes' and not medical_info_text:
        medical_info_text = 'Yes, has medical conditions'
    elif has_conditions == 'no':
        medical_info_text = 'No medical conditions reported'
    
    # Update user with medical information
    cur.execute("""
        UPDATE users
        SET medical_conditions=%s
        WHERE id=%s
    """, (medical_info_text, user_id))
    
    conn.commit()
    conn.close()
    
    return redirect('/user')


@user_bp.route('/payment_history')
def payment_history():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Get user info
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        return redirect('/login')
    
    # Get all payments for this user
    cur.execute("""
        SELECT id, user_id, amount, payment_type, transaction_id, payment_date
        FROM payments
        WHERE user_id=%s
        ORDER BY payment_date DESC
    """, (user_id,))
    
    payments = cur.fetchall()
    conn.close()
    
    # Calculate period information and totals
    period_start = None
    period_end = None
    membership_total = 0
    facility_total = 0
    
    if payments:
        # Sort payments by date to find earliest and latest
        sorted_payments = sorted(payments, key=lambda x: x['payment_date'])
        period_start = sorted_payments[0]['payment_date']
        period_end = sorted_payments[-1]['payment_date']
        
        # Calculate totals by payment type
        for payment in payments:
            amount = float(payment['amount'])
            if payment['payment_type'] == 'membership':
                membership_total += amount
            else:
                facility_total += amount
    
    all_total = membership_total + facility_total
    
    return render_template('payment_history.html', 
                         user=user, 
                         payments=payments,
                         period_start=period_start,
                         period_end=period_end,
                         membership_total=membership_total,
                         facility_total=facility_total,
                         all_total=all_total)

@user_bp.route('/grounds')
def grounds():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        return redirect('/login')
    
    # Get all active grounds
    cur.execute("SELECT * FROM grounds WHERE is_active=1 ORDER BY name")
    grounds_list = cur.fetchall()
    
    conn.close()
    
    return render_template('grounds.html', user=user, grounds=grounds_list)


@user_bp.route('/book_ground/<int:ground_id>', methods=['GET', 'POST'])
def book_ground(ground_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Get ground details
    cur.execute("SELECT * FROM grounds WHERE id=%s AND is_active=1", (ground_id,))
    ground = cur.fetchone()
    
    if not ground:
        conn.close()
        return render_template('error.html',
                             error='Ground Not Found',
                             message='The ground you are trying to book does not exist.')
    
    if request.method == 'GET':
        conn.close()
        return render_template('book_ground.html', ground=ground)
    
    # Process booking
    booking_date = request.form.get('booking_date', '').strip()
    booking_time = request.form.get('booking_time', '').strip()
    
    # Validation
    if not booking_date or not booking_time:
        conn.close()
        return render_template('book_ground.html',
                             ground=ground,
                             error='Please select both date and time.')
    
    # Validate date format (YYYY-MM-DD)
    try:
        from datetime import datetime
        booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
        if booking_date_obj < date.today():
            conn.close()
            return render_template('book_ground.html',
                                 ground=ground,
                                 error='Cannot book for past dates. Please select a future date.')
    except ValueError:
        conn.close()
        return render_template('book_ground.html',
                             ground=ground,
                             error='Invalid date format.')
    
    # Check if time slot is already booked
    cur.execute("""
        SELECT id FROM ground_bookings
        WHERE ground_id=%s AND booking_date=%s AND booking_time=%s
    """, (ground_id, booking_date, booking_time))
    
    existing_booking = cur.fetchone()
    
    if existing_booking:
        conn.close()
        return render_template('book_ground.html',
                             ground=ground,
                             error=f'This time slot ({booking_time}) is already booked for {booking_date}. Please select a different time.')
    
    # Create booking
    try:
        cur.execute("""
            INSERT INTO ground_bookings (user_id, ground_id, booking_date, booking_time)
            VALUES (%s, %s, %s, %s)
        """, (user_id, ground_id, booking_date, booking_time))
        
        conn.commit()
        conn.close()
        
        return render_template('booking_confirmed.html',
                             ground_name=ground['name'],
                             booking_date=booking_date,
                             booking_time=booking_time)
    
    except Exception as e:
        conn.close()
        return render_template('book_ground.html',
                             ground=ground,
                             error='An error occurred while booking. Please try again.')


@user_bp.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        return redirect('/login')
    
    # Get all bookings for this user, ordered by date and time
    cur.execute("""
        SELECT gb.id, g.name, gb.booking_date, gb.booking_time, gb.created_at
        FROM ground_bookings gb
        JOIN grounds g ON gb.ground_id = g.id
        WHERE gb.user_id=%s
        ORDER BY gb.booking_date DESC, gb.booking_time DESC
    """, (user_id,))
    
    bookings = cur.fetchall()
    conn.close()
    
    return render_template('my_bookings.html', user=user, bookings=bookings)


@user_bp.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Verify booking belongs to user
    cur.execute("""
        SELECT user_id FROM ground_bookings
        WHERE id=%s
    """, (booking_id,))
    
    booking = cur.fetchone()
    
    if not booking or booking['user_id'] != user_id:
        conn.close()
        return redirect('/my_bookings')
    
    # Delete booking
    cur.execute("DELETE FROM ground_bookings WHERE id=%s", (booking_id,))
    conn.commit()
    conn.close()
    
    return redirect('/my_bookings')