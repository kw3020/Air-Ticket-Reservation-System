"""
Kevin Wang - kw3020
CS-UY 3083 Project
Air Ticket Reservation System
"""

import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'e air ticket reservation system'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register_staff', methods=['GET', 'POST'])
def register_staff():
    if request.method == 'POST':
        email = request.form.get('email')  # Use email as the identifier
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        date_of_birth = request.form.get('date_of_birth')
        phone_number = request.form.get('phone_number')
        airline_name = request.form.get('airline_name')

        hashed_password = hashlib.md5(password.encode()).hexdigest()

        cursor = mysql.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO airlinestaff (email, password, first_name, last_name, date_of_birth, phone_number, airline_name) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (email, hashed_password, first_name, last_name, date_of_birth, phone_number, airline_name))
            mysql.connection.commit()
            flash('Airline staff registration successful')
        except Exception as e:
            flash('Registration failed: ' + str(e))
        finally:
            cursor.close()

        return redirect(url_for('login'))

    return render_template('register_staff.html')



@app.route('/register_customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        building_number = request.form.get('building_number')
        street_name = request.form.get('street_name')
        apartment_number = request.form.get('apartment_number')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip_code')
        phone_number = request.form.get('phone_number')
        passport_number = request.form.get('passport_number')
        passport_expiration = request.form.get('passport_expiration')
        passport_country = request.form.get('passport_country')
        date_of_birth = request.form.get('date_of_birth')

        hashed_password = hashlib.md5(password.encode()).hexdigest()

        cursor = mysql.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO customer (email, password, first_name, last_name, building_number, street_name, apartment_number, city, state, zip_code, phone_number, passport_number, passport_expiration, passport_country, date_of_birth) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (email, hashed_password, first_name, last_name, building_number, street_name, apartment_number, city, state, zip_code, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
            mysql.connection.commit()
            flash('Registration successful')
        except Exception as e:
            flash('Registration failed: ' + str(e))
        finally:
            cursor.close()
        
        return redirect(url_for('login'))

    return render_template('register_customer.html')


@app.route('/search_flights', methods=['GET', 'POST'])
def search_flights():
    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        departure_date = request.form.get('departure_date')

        cursor = mysql.connection.cursor()
        try:
            query = """
            SELECT * FROM flight 
            WHERE departure_airport_code = %s 
            AND arrival_airport_code = %s 
            AND departure_date_and_time LIKE %s
            """
            formatted_date = departure_date + "%"  # Adds the wildcard character for LIKE
            cursor.execute(query, (source, destination, formatted_date))
            flights = cursor.fetchall()
            if not flights:
                flash('No flights found.')
        except Exception as e:
            flash('Error: ' + str(e))
        finally:
            cursor.close()

        return render_template('flight_results.html', flights=flights)

    return render_template('search_flights.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        cursor = mysql.connection.cursor()
        # Check in customer table
        cursor.execute("SELECT * FROM customer WHERE email = %s", [email])
        user = cursor.fetchone()

        if not user:
            # If not found, check in airlinestaff table
            cursor.execute("SELECT * FROM airlinestaff WHERE email = %s", [email])
            user = cursor.fetchone()

        cursor.close()

        if user and hashlib.md5(password.encode()).hexdigest() == user['password']:
            session['logged_in'] = True
            session['user_email'] = email
            session['user_type'] = 'staff' if 'airline_name' in user else 'customer'
            if 'airline_name' in user:
                session['user_airline'] = user['airline_name']
                return redirect(url_for('staff_homepage'))
            else:
                return redirect(url_for('customer_homepage'))
        else:
            flash('Login failed. Check your email and password.')
    return render_template('login.html')

@app.route('/customer_homepage')
def customer_homepage():
    if 'logged_in' in session and session['user_type'] == 'customer':
        return render_template('customer_homepage.html')
    else:
        flash('Access denied. Please log in as a customer.')
        return redirect(url_for('login'))
    
@app.route('/customer_homepage/view_my_flights')
def view_my_flights():
    if 'logged_in' in session and session['user_type'] == 'customer':
        email = session['user_email']
        cursor = mysql.connection.cursor()

        # Fetch upcoming flights
        cursor.execute("""
            SELECT t.*, f.departure_date_and_time, f.arrival_date_and_time, 
                   f.departure_airport_code, f.arrival_airport_code, f.status
            FROM ticket t
            JOIN flight f ON t.flight_number = f.flight_number
            WHERE t.email = %s AND f.departure_date_and_time > NOW()
            ORDER BY f.departure_date_and_time
            """, [email])
        upcoming_flights = cursor.fetchall()

        # Fetch past flights
        cursor.execute("""
            SELECT t.*, f.departure_date_and_time, f.arrival_date_and_time, 
                   f.departure_airport_code, f.arrival_airport_code, f.status
            FROM ticket t
            JOIN flight f ON t.flight_number = f.flight_number
            WHERE t.email = %s AND f.departure_date_and_time < NOW()
            ORDER BY f.departure_date_and_time DESC
            """, [email])
        past_flights = cursor.fetchall()

        cursor.close()
        return render_template('view_my_flights.html', upcoming_flights=upcoming_flights, past_flights=past_flights)
    else:
        flash('Please log in to view your flights.')
        return redirect(url_for('login'))


@app.route('/cancel_trip/<int:ticket_id>')
def cancel_trip(ticket_id):
    if 'logged_in' in session and session['user_type'] == 'customer':
        email = session['user_email']
        cursor = mysql.connection.cursor()
        # Check if the ticket belongs to the user and the flight is more than 24 hours away
        cursor.execute("""
            SELECT * FROM ticket 
            WHERE ticket_ID = %s AND email = %s AND flight_departure_date_and_time > NOW() + INTERVAL 1 DAY
            """, (ticket_id, email))
        ticket = cursor.fetchone()
        if ticket:
            # Delete the ticket record for this user
            cursor.execute("DELETE FROM ticket WHERE ticket_ID = %s", [ticket_id])
            # Optionally, delete related payment record if exists
            cursor.execute("DELETE FROM payment WHERE ticket_ID = %s", [ticket_id])
            mysql.connection.commit()
            flash('Your ticket has been successfully cancelled.')
        else:
            flash('Cancellation failed or you are not authorized.')
        cursor.close()
        return redirect(url_for('view_my_flights'))
    else:
        flash('Please log in to cancel a trip.')
        return redirect(url_for('login'))


@app.route('/select_flight_to_purchase')
def select_flight_to_purchase():
    if 'logged_in' in session and session['user_type'] == 'customer':
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT flight_number, departure_date_and_time, arrival_date_and_time, departure_airport_code, arrival_airport_code, base_price 
            FROM flight 
            WHERE departure_date_and_time > NOW()
            """)
        flights = cursor.fetchall()
        cursor.close()
        return render_template('select_flight.html', flights=flights)
    else:
        flash('Please log in to view available flights.')
        return redirect(url_for('login'))


@app.route('/purchase_ticket/<string:flight_number>', methods=['GET', 'POST'])
def purchase_ticket(flight_number):
    if 'logged_in' in session and session['user_type'] == 'customer':
        email = session['user_email']

        cursor = mysql.connection.cursor()
        # Fetch customer details
        cursor.execute("SELECT first_name, last_name, date_of_birth FROM customer WHERE email = %s", [email])
        customer = cursor.fetchone()

        # Fetch flight departure date and time
        cursor.execute("SELECT departure_date_and_time FROM flight WHERE flight_number = %s", [flight_number])
        flight = cursor.fetchone()

        if request.method == 'POST':
            card_type = request.form['card_type']
            card_number = request.form['card_number']
            name_on_card = request.form['name_on_card']
            expiration_date = request.form['expiration_date']

            # Calculate final price (modify this logic as per your requirement)
            cursor.execute("SELECT base_price FROM flight WHERE flight_number = %s", [flight_number])
            flight_data = cursor.fetchone()
            base_price = flight_data['base_price'] if flight_data else 0
            final_price = base_price  # Example calculation, adjust as needed

            # Insert ticket details
            cursor.execute("""
                INSERT INTO ticket (email, first_name, last_name, date_of_birth, flight_number, flight_departure_date_and_time, calculated_price, purchase_date_and_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, (email, customer['first_name'], customer['last_name'], customer['date_of_birth'], flight_number, flight['departure_date_and_time'], final_price))
            ticket_id = cursor.lastrowid

            # Insert payment details
            cursor.execute("""
                INSERT INTO payment (card_type, card_number, name_on_card, expiration_date, ticket_ID)
                VALUES (%s, %s, %s, %s, %s)
                """, (card_type, card_number, name_on_card, expiration_date, ticket_id))

            mysql.connection.commit()
            cursor.close()

            flash('Ticket purchased successfully!')
            return redirect(url_for('purchase_confirmation', ticket_id=ticket_id))

        return render_template('purchase_ticket.html', flight_number=flight_number)
    else:
        flash('Please log in to purchase tickets.')
        return redirect(url_for('login'))


    
@app.route('/purchase_confirmation/<int:ticket_id>')
def purchase_confirmation(ticket_id):
    if 'logged_in' in session and session['user_type'] == 'customer':
        # You can add additional logic here if needed
        return render_template('purchase_confirmation.html', ticket_id=ticket_id)
    else:
        flash('Please log in.')
        return redirect(url_for('login'))



@app.route('/search_flight_status', methods=['GET', 'POST'])
def search_flight_status():
    if request.method == 'POST':
        airline_name = request.form.get('airline_name')
        flight_number = request.form.get('flight_number')
        date = request.form.get('date')

        if not date:
            flash('Please enter a date.')
            return redirect(url_for('search_flight_status'))

        cursor = mysql.connection.cursor()
        query = """
        SELECT * FROM flight 
        WHERE airline_name = %s 
        AND flight_number = %s 
        AND DATE(departure_date_and_time) = %s
        """
        cursor.execute(query, (airline_name, flight_number, date))
        flight_status = cursor.fetchall()
        cursor.close()

        return render_template('flight_status_results.html', flight_status=flight_status)

    return render_template('search_flight_status.html')

@app.route('/leave_comment/<string:flight_number>/<string:departure_date_and_time>', methods=['GET', 'POST'])
def leave_comment(flight_number, departure_date_and_time):
    if 'logged_in' in session and session['user_type'] == 'customer':
        email = session['user_email']
        if request.method == 'POST':
            rating = request.form['rating']
            comment = request.form['comment']
            cursor = mysql.connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO rating_comment (email, flight_number, departure_date_and_time, rating, comment, airline_name)
                    VALUES (%s, %s, %s, %s, %s, (SELECT airline_name FROM flight WHERE flight_number = %s))
                    """, (email, flight_number, departure_date_and_time, rating, comment, flight_number))
                mysql.connection.commit()
                flash('Your comment and rating have been submitted.')
            except Exception as e:
                flash('Error: ' + str(e))
            finally:
                cursor.close()
            return redirect(url_for('view_my_flights'))
        
        return render_template('leave_comment.html', flight_number=flight_number, departure_date_and_time=departure_date_and_time)
    else:
        flash('Please log in.')
        return redirect(url_for('login'))


@app.route('/track_spending', methods=['GET', 'POST'])
def track_spending():
    if 'logged_in' in session and session['user_type'] == 'customer':
        email = session['user_email']

        # Default range: past year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        custom_spending = None

        cursor = mysql.connection.cursor()

        # Query for total spending in the past year
        cursor.execute("""
            SELECT SUM(calculated_price) FROM ticket
            WHERE email = %s AND purchase_date_and_time BETWEEN %s AND %s
            """, (email, start_date, end_date))
        result = cursor.fetchone()
        total_spending = result['SUM(calculated_price)'] if result else 0


        if request.method == 'POST':
            # Update range if custom dates are provided
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')

            # Query for custom range spending
            cursor.execute("""
                SELECT SUM(calculated_price) FROM ticket
                WHERE email = %s AND purchase_date_and_time BETWEEN %s AND %s
                """, (email, start_date, end_date))
            result = cursor.fetchone()
            custom_spending = result[0] if result and result[0] else 0

        # Month-wise spending for the last six months
        cursor.execute("""
            SELECT MONTH(purchase_date_and_time) as month, SUM(calculated_price) as total
            FROM ticket
            WHERE email = %s AND purchase_date_and_time BETWEEN DATE_SUB(NOW(), INTERVAL 6 MONTH) AND NOW()
            GROUP BY MONTH(purchase_date_and_time)
            """, [email])
        monthly_data = cursor.fetchall()

        # Prepare data for Chart.js
        months = [datetime(2000, month['month'], 1).strftime('%B') for month in monthly_data]
        spending_values = [month['total'] for month in monthly_data]

        cursor.close()
        return render_template('track_spending.html', total_spending=total_spending, 
                               custom_spending=custom_spending, months=months, spending_values=spending_values, 
                               start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))
    else:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))


@app.route('/staff_homepage')
def staff_homepage():
    if 'logged_in' in session and session['user_type'] == 'staff':
        return render_template('staff_homepage.html')
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))

@app.route('/create_flight', methods=['GET', 'POST'])
def create_flight():
    if 'logged_in' in session and session['user_type'] == 'staff':
        if request.method == 'POST':
            flight_number = request.form.get('flight_number')
            departure_date_and_time = request.form.get('departure_date_and_time')
            arrival_date_and_time = request.form.get('arrival_date_and_time')
            departure_airport_code = request.form.get('departure_airport_code')
            arrival_airport_code = request.form.get('arrival_airport_code')
            base_price = request.form.get('base_price')  # Retrieving base_price from form
            airplane_id = request.form.get('airplane_id')
            status = request.form.get('status')
            airline_name = session['user_airline']

            cursor = mysql.connection.cursor()

            # Check for airplane maintenance
            cursor.execute("""
                SELECT * FROM maintenance 
                WHERE airplane_id = %s AND 
                start_date_and_time <= NOW() AND 
                end_date_and_time >= NOW()
                """, [airplane_id])
            maintenance = cursor.fetchone()

            if maintenance:
                flash('Cannot schedule flight. Airplane is under maintenance.')
                return redirect(url_for('create_flight'))

            try:
                # Inserting new flight data into the flight table
                cursor.execute("""
                    INSERT INTO flight (flight_number, departure_date_and_time, arrival_date_and_time, departure_airport_code, arrival_airport_code, base_price, airplane_id, status, airline_name) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (flight_number, departure_date_and_time, arrival_date_and_time, departure_airport_code, arrival_airport_code, base_price, airplane_id, status, airline_name))
                mysql.connection.commit()
                flash('New flight created successfully.')
            except Exception as e:
                flash('Error creating flight: ' + str(e))
            finally:
                cursor.close()
            return redirect(url_for('staff_homepage'))

        return render_template('create_flight.html')
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))

@app.route('/change_flight_status/<string:flight_number>', methods=['GET', 'POST'])
def change_flight_status(flight_number):
    if 'logged_in' in session and session['user_type'] == 'staff':
        if request.method == 'POST':
            new_status = request.form.get('status')
            cursor = mysql.connection.cursor()
            try:
                cursor.execute("""
                UPDATE flight SET status = %s
                WHERE flight_number = %s
                """, (new_status, flight_number))
                mysql.connection.commit()
                flash('Flight status updated successfully.')
            except Exception as e:
                flash('Error updating flight status: ' + str(e))
            finally:
                cursor.close()
            return redirect(url_for('view_flights'))
        return render_template('change_flight_status.html', flight_number=flight_number)
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))

@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    if 'logged_in' in session and session['user_type'] == 'staff':
        if request.method == 'POST':
            # Extract airplane data from form
            airplane_id = request.form.get('airplane_id')
            number_of_seats = request.form.get('number_of_seats')
            manufacturing_company = request.form.get('manufacturing_company')
            model_number = request.form.get('model_number')
            manufacturing_date = request.form.get('manufacturing_date')
            airline_name = session['user_airline']  # Get airline from session

            cursor = mysql.connection.cursor()
            try:
                cursor.execute("""
                INSERT INTO airplane (airplane_id, number_of_seats, manufacturing_company, model_number, manufacturing_date, airline_name) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (airplane_id, number_of_seats, manufacturing_company, model_number, manufacturing_date, airline_name))
                mysql.connection.commit()
                flash('New airplane added successfully.')
            except Exception as e:
                flash('Error adding airplane: ' + str(e))
            finally:
                cursor.close()
            return redirect(url_for('view_airplanes'))
        return render_template('add_airplane.html')
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))
    
@app.route('/view_airplanes')
def view_airplanes():
    if 'logged_in' in session and session['user_type'] == 'staff':
        airline_name = session['user_airline']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM airplane WHERE airline_name = %s", [airline_name])
        airplanes = cursor.fetchall()
        cursor.close()
        return render_template('view_airplanes.html', airplanes=airplanes)
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))
    
@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
    if 'logged_in' in session and session['user_type'] == 'staff':
        if request.method == 'POST':
            # Extract airport data from form
            code = request.form.get('code')
            name = request.form.get('name')
            city = request.form.get('city')
            country = request.form.get('country')
            number_of_terminals = request.form.get('number_of_terminals')
            airport_type = request.form.get('airport_type')

            cursor = mysql.connection.cursor()
            try:
                cursor.execute("""
                INSERT INTO airport (code, name, city, country, number_of_terminals, airport_type) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (code, name, city, country, number_of_terminals, airport_type))
                mysql.connection.commit()
                flash('New airport added successfully.')
            except Exception as e:
                flash('Error adding airport: ' + str(e))
            finally:
                cursor.close()
            return redirect(url_for('staff_homepage'))
        return render_template('add_airport.html')
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))

@app.route('/schedule_maintenance', methods=['GET', 'POST'])
def schedule_maintenance():
    if 'logged_in' in session and session['user_type'] == 'staff':
        if request.method == 'POST':
            # Extract maintenance data from form
            airplane_id = request.form.get('airplane_id')
            start_date_and_time = request.form.get('start_date_and_time')
            end_date_and_time = request.form.get('end_date_and_time')

            cursor = mysql.connection.cursor()
            try:
                cursor.execute("""
                INSERT INTO maintenance (airplane_id, start_date_and_time, end_date_and_time) 
                VALUES (%s, %s, %s)
                """, (airplane_id, start_date_and_time, end_date_and_time))
                mysql.connection.commit()
                flash('Maintenance scheduled successfully.')
            except Exception as e:
                flash('Error scheduling maintenance: ' + str(e))
            finally:
                cursor.close()
            return redirect(url_for('staff_homepage'))
        return render_template('schedule_maintenance.html')
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))

@app.route('/view_frequent_customers')
def view_frequent_customers():
    if 'logged_in' in session and session['user_type'] == 'staff':
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("""
            SELECT customer.email, COUNT(*) as flight_count 
            FROM customer 
            JOIN ticket ON customer.email = ticket.email 
            WHERE ticket.purchase_date_and_time > NOW() - INTERVAL 1 YEAR 
            GROUP BY customer.email 
            ORDER BY flight_count DESC
            """)
            customers = cursor.fetchall()
        except Exception as e:
            flash('Error: ' + str(e))
        finally:
            cursor.close()
        return render_template('view_frequent_customers.html', customers=customers)
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))

@app.route('/view_customer_flights/<string:email>')
def view_customer_flights(email):
    if 'logged_in' in session and session['user_type'] == 'staff':
        email = request.form.get('email')
        airline_name = session['user_airline']
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("""
            SELECT flight.* 
            FROM flight 
            JOIN ticket ON flight.flight_number = ticket.flight_number 
            WHERE ticket.email = %s AND flight.airline_name = %s
            """, (email, airline_name))
            flights = cursor.fetchall()
        except Exception as e:
            flash('Error: ' + str(e))
        finally:
            cursor.close()
        return render_template('view_customer_flights.html', flights=flights, customer_email=email)
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))

@app.route('/staff_homepage/view_flights', methods=['GET', 'POST'])
def view_flights():
    if 'logged_in' in session and session['user_type'] == 'staff':
        airline_name = session['user_airline']  # Assuming you store the airline name in session
        cursor = mysql.connection.cursor()

        if request.method == 'POST':
            # Filter based on form input (date range, source/destination)
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            source = request.form.get('source')
            destination = request.form.get('destination')

            query = """
            SELECT * FROM flight
            WHERE airline_name = %s AND 
            departure_date_and_time BETWEEN %s AND %s AND 
            departure_airport_code LIKE %s AND 
            arrival_airport_code LIKE %s
            """
            cursor.execute(query, (airline_name, start_date, end_date, source+'%', destination+'%'))

        else:
            # Default view for the next 30 days
            query = """
            SELECT * FROM flight 
            WHERE airline_name = %s AND 
            departure_date_and_time BETWEEN NOW() AND NOW() + INTERVAL 30 DAY
            """
            cursor.execute(query, [airline_name])

        flights = cursor.fetchall()
        cursor.close()
        return render_template('view_flights.html', flights=flights)
    else:
        flash('Access denied. Please log in as airline staff.')
        return redirect(url_for('login'))

@app.route('/view_customers/<string:flight_number>')
def view_customers(flight_number):
    if 'logged_in' in session and session['user_type'] == 'staff':
        cursor = mysql.connection.cursor()
        try:
            query = """
            SELECT customer.* FROM customer
            JOIN ticket ON customer.email = ticket.email
            WHERE ticket.flight_number = %s
            """
            cursor.execute(query, [flight_number])
            customers = cursor.fetchall()
        except Exception as e:
            flash('Error: ' + str(e))
        finally:
            cursor.close()
        return render_template('view_customers.html', customers=customers, flight_number=flight_number)
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))
    
@app.route('/view_comments/<string:flight_number>')
def view_comments(flight_number):
    if 'logged_in' in session and session['user_type'] == 'staff':
        cursor = mysql.connection.cursor()
        try:
            query = """
            SELECT * FROM rating_comment
            WHERE flight_number = %s
            """
            cursor.execute(query, [flight_number])
            comments = cursor.fetchall()
        except Exception as e:
            flash('Error: ' + str(e))
        finally:
            cursor.close()
        return render_template('view_comments.html', comments=comments, flight_number=flight_number)
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))

@app.route('/view_revenue')
def view_revenue():
    if 'logged_in' in session and session['user_type'] == 'staff':
        airline_name = session['user_airline']
        cursor = mysql.connection.cursor()

        # Query for last month's revenue
        cursor.execute("""
            SELECT SUM(calculated_price) as total FROM ticket
            JOIN flight ON ticket.flight_number = flight.flight_number
            WHERE flight.airline_name = %s AND 
            purchase_date_and_time BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW()
            """, [airline_name])
        result = cursor.fetchone()
        last_month_revenue = result['total'] if result else 0

        # Query for last year's revenue
        cursor.execute("""
            SELECT SUM(calculated_price) as total FROM ticket
            JOIN flight ON ticket.flight_number = flight.flight_number
            WHERE flight.airline_name = %s AND 
            purchase_date_and_time BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW()
            """, [airline_name])
        result = cursor.fetchone()
        last_year_revenue = result['total'] if result else 0

        cursor.close()
        return render_template('view_revenue.html', last_month_revenue=last_month_revenue, 
                               last_year_revenue=last_year_revenue)
    else:
        flash('Access denied. Please log in as staff.')
        return redirect(url_for('login'))



@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
