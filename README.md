# CS50x Finance Web Application

This is a web application for managing stock portfolios and tracking real-time stock prices that I built as part of Harvard's CS50x course.

## Features

- **User Authentication**
  - Register new accounts with username and password
  - Login/logout functionality
  - Change password capability
  - Session-based user management

- **Stock Trading**
  - Get real-time stock quotes via Yahoo Finance API
  - Buy shares of stocks
  - Sell shares from portfolio
  - View detailed transaction history

- **Portfolio Management**
  - View current portfolio of stocks
  - Track total portfolio value
  - Monitor cash balance
  - Add additional cash (capped at $10,000)

## Technologies Used

- **Backend**
  - Python
  - Flask web framework
  - SQLite database
  - CS50 Library
  - Flask-Session for session management

- **Frontend**
  - HTML5
  - CSS3
  - Bootstrap 5.3
  - Jinja2 templating

- **External APIs**
  - Yahoo Finance API for real-time stock data

## Installation

1. Ensure you have Python installed on your system

2. Clone this repository:
```bash
git clone <your-repository-url>
cd Finance
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask application:
```bash
flask run
```

5. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Register for a new account
2. Log in with your credentials
3. Use the navigation bar to:
   - Get stock quotes
   - Buy stocks
   - Sell stocks
   - View transaction history
   - Add cash to your account
   - Change your password

## Project Structure

```
Finance/
├── app.py              # Main application file
├── helpers.py          # Helper functions
├── requirements.txt    # Project dependencies
├── finance.db         # SQLite database
├── static/            # Static files (CSS, images)
└── templates/         # HTML templates
```

## Security Features

- Passwords are hashed using Werkzeug's security functions
- Session-based authentication
- CSRF protection
- Input validation for all forms
- Secure password change functionality

## Database Schema

The application uses SQLite with the following main tables:
- `users`: Stores user information and cash balance
- `transactions`: Records all buy/sell transactions
