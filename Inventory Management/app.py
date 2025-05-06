from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'dharani@2004'
app.config['MYSQL_DB'] = 'moni'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def view_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Product")
    products = cur.fetchall()
    cur.close()
    return render_template('products.html', products=products)
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Product (product_name) VALUES (%s)", (product_name,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('view_products'))
    return render_template('add_product.html')

@app.route('/locations')
def view_locations():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Location")
    locations = cur.fetchall()
    cur.close()
    return render_template('locations.html', locations=locations)

@app.route('/add_location', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location_name = request.form['location_name']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Location (location_name) VALUES (%s)", (location_name,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('view_locations'))
    return render_template('add_location.html')

@app.route('/movements')
def view_movements():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ProductMovement")
    movements = cur.fetchall()
    cur.close()
    return render_template('movements.html', movements=movements)

@app.route('/add_movement', methods=['GET', 'POST'])
def add_movement():
    if request.method == 'POST':
        from_location = request.form.get('from_location') or None
        to_location = request.form.get('to_location') or None
        product_id = request.form['product_id']
        qty = int(request.form['qty'])
        timestamp = datetime.now()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO ProductMovement (timestamp, from_location, to_location, product_id, qty) VALUES (%s, %s, %s, %s, %s)",
                    (timestamp, from_location, to_location, product_id, qty))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('view_movements'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT product_id, product_name FROM Product")
    products = cur.fetchall()
    cur.execute("SELECT location_id, location_name FROM Location")
    locations = cur.fetchall()
    cur.close()
    return render_template('add_movement.html', products=products, locations=locations)


@app.route('/report')
def report():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            p.product_name,
            l.location_name,
            COALESCE(SUM(CASE WHEN pm.to_location = l.location_id THEN pm.qty ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN pm.from_location = l.location_id THEN pm.qty ELSE 0 END), 0) AS balance
        FROM Product p
        CROSS JOIN Location l
        LEFT JOIN ProductMovement pm 
            ON p.product_id = pm.product_id 
            AND (pm.to_location = l.location_id OR pm.from_location = l.location_id)
        GROUP BY p.product_name, l.location_name
    """)
    report_data = cur.fetchall()
    cur.close()
    return render_template('report.html', report_data=report_data)


if __name__ == '__main__':
    app.run(debug=True)
