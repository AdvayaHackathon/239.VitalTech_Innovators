import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
# 1. Import Libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
from flask import request,flash
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=8,
    min_samples_split=10,
    min_samples_leaf=5,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)



rf_model = joblib.load(r"C:\HACKATHON_BGSCET\website\final_realistic_rf_ckd_model_lessaccurate_gender_fixed.pkl")




app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management


def get_user_by_email(email):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, email, password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

@app.route('/')
def first():
    return render_template("first.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)

        if user:
            user_id, user_email, user_password = user

            if user_password == password:   # Direct comparison (plain text password)
                session['user_id'] = user_id
                session['email'] = user_email
                return redirect(url_for('home'))
            else:
                error = "Invalid password."
        else:
            error = "User not found."

    return render_template('login.html', error=error)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            error = 'User with that email already exists.'
        else:
            # Insert new user into the database
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO users (name, email, password)
                    VALUES (?, ?, ?)
                """, (name, email, password))
                conn.commit()
                flash("✅ Signup successful! Please login.", "success")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = "An error occurred while signing up."
            finally:
                conn.close()

    return render_template('signup.html', error=error)

@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Collect form data
        input_data = {
            'age': float(request.form['age']),
            'bp': float(request.form['bp']),
            'sg': float(request.form['sg']),
            'al': float(request.form['al']),
            'su': float(request.form['su']),
            'rbc': int(request.form['rbc']),
            'pc': int(request.form['pc']),
            'pcc': int(request.form['pcc']),
            'ba': int(request.form['ba']),
            'bgr': float(request.form['bgr']),
            'bu': float(request.form['bu']),
            'sc': float(request.form['sc']),
            'sod': float(request.form['sod']),
            'pot': float(request.form['pot']),
            'hemo': float(request.form['hemo']),
            'pcv': float(request.form['pcv']),
            'wc': float(request.form['wc']),
            'rc': float(request.form['rc']),
            'htn': int(request.form['htn']),
            'dm': int(request.form['dm']),
            'cad': int(request.form['cad']),
            'appet': int(request.form['appet']),
            'pe': int(request.form['pe']),
            'ane': int(request.form['ane']),
            'gender':int(request.form['gender']),
            'egfr':float(request.form['egfr'])

        }
        


        # Create DataFrame for prediction
        input_features = pd.DataFrame([input_data])
        # Predict
        prediction = rf_model.predict(input_features)[0]
        if 'user_id' in session:
            user_id = session['user_id']
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO predictions (user_id, prediction_result, input_data)
                VALUES (?, ?, ?)
            """, (user_id, str(prediction), str(input_data)))
            conn.commit()
            conn.close()

        # Display result page
        return render_template('result.html', prediction=prediction)
    
    return render_template('predict.html')
@app.route('/past_predictions')
def past_predictions():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT prediction_result, input_data, prediction_time
        FROM predictions
        WHERE user_id = ?
        ORDER BY prediction_time DESC
    """, (user_id,))
    past_preds = cursor.fetchall()
    conn.close()

    return render_template('past_predictions.html', predictions=past_preds)


@app.route('/find_doctors', methods=['GET', 'POST'])
def find_doctors():
    if request.method == 'POST':
        # After patient submits city
        city = request.form['city'].title()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT doctor_id,name, hospital, contact FROM doctors WHERE city = ?", (city,))
        doctors = cursor.fetchall()
        conn.close()

        return render_template('doctors_list.html', city=city, doctors=doctors)
    else:
        # On normal GET request, show search page
        return render_template('find_doctors.html')

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    doctor_id = request.form['doctor_id']
    reason = request.form['reason']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert into appointments table
    cursor.execute("""
        INSERT INTO appointments (user_id, doctor_id, appointment_date, reason, status)
        VALUES (?, ?, datetime('now'), ?, 'Scheduled')
    """, (user_id, doctor_id, reason))

    conn.commit()
    conn.close()

    flash("✅ Appointment booked successfully!", "success")

    return redirect(url_for('find_doctors'))

@app.route('/appointments')
def appointments():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.name, d.hospital, d.contact, a.appointment_date, a.reason, a.status
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.user_id = ?
        ORDER BY a.appointment_date DESC
    """, (user_id,))
    
    appointments = cursor.fetchall()
    conn.close()

    return render_template('appointments.html', appointments=appointments)
@app.route("/care_tips")
def display():
    return render_template("care_tips.html")

if __name__ == '__main__':
    app.run(debug=True)