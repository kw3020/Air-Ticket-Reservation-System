"""
Kevin Wang - kw3020
CS-UY 3083 Project
Air Ticket Reservation System
"""

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change to a strong secret key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search-flights', methods=['GET', 'POST'])
def search_flights():
    if request.method == 'POST':
        # Extract search criteria from form data
        source = request.form.get('source')
        destination = request.form.get('destination')
        departure_date = request.form.get('departure_date')

        # Here you would query your database for flights matching the criteria
        # For now, let's return a placeholder list of flights
        flights = [{'flight_number': 'FL123', 'departure_airport': source, 'arrival_airport': destination, 'departure_date': departure_date}]
        return render_template('search_results.html', flights=flights)

    # GET request: just show the search form
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
