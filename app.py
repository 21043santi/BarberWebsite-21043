from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
# testing the changes

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'santi-styles-secure-67'

db = SQLAlchemy(app)

# --- MODELS ---
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    service = db.Column(db.String(100))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --- ROUTES ---
@app.route('/')
def home():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('index.html', reviews=reviews)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        return redirect(url_for('home'))
    return render_template('contact.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        # Takes the JSON data from the Javascript popup logic and sassssves it
        data = request.json
        new_booking = Booking(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            service=data.get('service'),
            date=data.get('date'),
            time=data.get('time')
        )
        db.session.add(new_booking)
        db.session.commit()
        return jsonify({'status': 'success'})
        
    return render_template('booking.html')

@app.route('/add-review', methods=['POST'])
def add_review():
    data = request.json
    new_review = Review(
        name=data.get('name'),
        rating=int(data.get('rating')),
        message=data.get('message')
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/delete-review/<int:id>')
def delete_review(id):
    review_to_delete = Review.query.get_or_404(id)
    try:
        db.session.delete(review_to_delete)
        db.session.commit()
    except Exception as e:
        pass
    return redirect(url_for('home'))

# --- ADMIN DASHBOARD ---
@app.route('/admin')
def admin_dashboard():
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    return render_template('admin.html', bookings=bookings)

@app.route('/admin/confirm/<int:id>')
def confirm_booking(id):
    b = Booking.query.get_or_404(id)
    if b:
        b.status = 'Confirmed'
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)