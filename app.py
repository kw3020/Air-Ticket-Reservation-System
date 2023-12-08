"""
Kevin Wang - kw3020
CS-UY 3083 Project
Air Ticket Reservation System
"""

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change to a strong secret key

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Leave blank if no password is set
app.config['MYSQL_DB'] = 'e air ticket reservation system'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # This is optional

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search-flights', methods=['GET', 'POST'])
def search_flights():
    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        departure_date = request.form.get('departure_date')

        cursor = mysql.connection.cursor()
        query = "SELECT * FROM flights WHERE departure_airport = %s AND arrival_airport = %s AND departure_date = %s"
        cursor.execute(query, (source, destination, departure_date))
        flights = cursor.fetchall()
        cursor.close()

        return render_template('search_results.html', flights=flights)

    return render_template('search_flights.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Here you should verify the username and password with your database
        # If the user is authenticated, set the session variable
        session['logged_in'] = True
        return redirect(url_for('protected'))

    # GET request: show the login form
    return render_template('login.html')

@app.route('/protected')
def protected():
    if session.get('logged_in'):
        return render_template('protected.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
