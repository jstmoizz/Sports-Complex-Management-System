# NUST Sports Complex Management System

A comprehensive Flask-based web application for managing sports complex facilities, memberships, ground bookings, and payments.

## Features

- **User Management**: Register and manage user accounts with role-based access control
- **Membership System**: Handle membership activation, deactivation, and renewal
- **Facilities Management**: Manage multiple facilities (Swimming, Gym, Horse Riding) with monthly fees
- **Ground Bookings**: Book sports grounds (Football, Basketball, Volleyball, Tennis, Badminton) with time slots
- **Payment Tracking**: Record and track membership and facility payments with transaction IDs
- **Medical Information**: Store and display user medical conditions for safety
- **Admin Dashboard**: Comprehensive dashboard for administrators to manage all aspects of the complex
- **User Dashboard**: Personal dashboard for users to view bookings and memberships

## Project Structure

```
SportsComplexMS/
├── main/
│   ├── app.py              # Flask application entry point
│   ├── config.py           # Configuration settings
│   ├── db.py               # Database connection utilities
│   ├── db_test.py          # Database testing utilities
│   └── migrate_db.py       # Database migration scripts
├── routes/
│   ├── auth.py             # Authentication routes (login, register, logout)
│   ├── user.py             # User dashboard and booking routes
│   └── admin.py            # Admin dashboard and management routes
├── templates/
│   ├── admin_dashboard.html      # Admin dashboard interface
│   ├── user_dashboard.html       # User dashboard interface
│   ├── login.html                # Login page
│   ├── register.html             # User registration page
│   ├── book_ground.html          # Ground booking page
│   ├── grounds.html              # Available grounds listing
│   ├── my_bookings.html          # User's bookings history
│   ├── medical_info.html         # Medical information form
│   ├── payment_confirmation.html # Payment confirmation page
│   ├── payment_history.html      # User payment history
│   ├── payment_success.html      # Payment success page
│   ├── payment_verified.html     # Payment verification page
│   ├── booking_confirmed.html    # Booking confirmation page
│   └── error.html                # Error page
└── Reference Database/
    └── database.sql        # Database schema and initialization
```

## Database Schema

### Users Table
- Stores user information including full name, email, CMS ID, password
- Tracks membership status and dates
- Stores medical conditions for safety purposes
- Role-based access (admin/user)

### Facilities Table
- Available facilities: Swimming, Gym, Horse Riding
- Tracks monthly fees and active status
- Linked to users via Many-to-Many relationship

### User Facilities Table
- Associates users with facilities
- Tracks facility access start date and last payment date

### Grounds Table
- Available grounds: Football, Basketball, Volleyball, Tennis, Badminton
- Active status tracking

### Ground Bookings Table
- Records ground bookings with date and time
- Unique constraint ensures no double-booking of same ground/time

### Payments Table
- Records all transactions (membership and facility)
- Stores transaction ID, amount, and payment date

## Setup Instructions

### Prerequisites
- Python 3.8+
- MySQL Server
- Virtual Environment

### Installation

1. **Clone the repository**
   ```bash
   cd c:\Users\amoiz\PycharmProjects\SportsComplexMS
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask mysql-connector-python
   ```

4. **Setup Database**
   - Open MySQL
   - Execute the SQL script from `Reference Database/database.sql`:
   ```bash
   mysql -u root -p < "Reference Database/database.sql"
   ```

5. **Configure Database Connection**
   - Update `main/config.py` with your MySQL credentials:
   ```python
   DB_HOST = 'localhost'
   DB_USER = 'root'
   DB_PASSWORD = 'your_password'
   DB_NAME = 'sports_complex'
   ```

## Running the Application

1. **Activate virtual environment**
   ```bash
   .venv\Scripts\activate
   ```

2. **Run the Flask application**
   ```bash
   python main/app.py
   ```

3. **Access the application**
   - Open browser and navigate to: `http://localhost:5000`

## Default Admin Account

- **Email**: admin@sports.com
- **Password**: admin123

## User Workflows

### User Registration and Login
1. Navigate to register page
2. Fill in personal information including medical conditions
3. Account created with default 'user' role
4. Login with email and password

### Booking a Ground
1. Login as user
2. Navigate to grounds page
3. Select ground, date, and time slot
4. Confirm booking

### Managing Membership
1. View membership status in user dashboard
2. Activate or renew membership
3. Track payment history

### Medical Information
1. Users can update medical conditions during registration
2. Admin can view all users' medical information in admin dashboard

## Admin Dashboard Features

- **Members & Memberships**: View all users, their membership status, and medical conditions
- **Payment Transactions**: Track all facility payment transactions
- **Facilities Management**: Add/delete facilities and manage fees
- **Ground Bookings**: View all ground bookings
- **User Facility Access**: Manage user access to facilities

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based with password hashing (SHA2-256)

## Security Features

- SHA2-256 password hashing
- Session-based authentication
- Role-based access control
- CSRF protection considerations
- Input validation

## Error Handling

The application includes comprehensive error handling with user-friendly error pages displaying:
- Database errors
- Authentication failures
- Invalid operations
- Form validation errors

## Future Enhancements

- Payment gateway integration
- Email notifications
- SMS alerts
- Advanced reporting and analytics
- Mobile app support
- QR code-based check-in system
- Automated payment reminders
