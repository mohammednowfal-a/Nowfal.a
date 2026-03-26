from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import csv, os, sqlite3, hashlib, json, random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'medipredict_super_secret_2024'

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'users.db')
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'data', 'diseases.csv')

HEALTH_TIPS = [
    "💧 Drink at least 8 glasses of water every day to stay hydrated.",
    "🚶 Walk 30 minutes daily to keep your heart healthy.",
    "🥦 Eat 5 servings of fruits and vegetables every day.",
    "😴 Get 7–9 hours of sleep each night for optimal health.",
    "🧘 Practice deep breathing for 5 minutes to reduce stress.",
    "🦷 Brush and floss your teeth twice a day.",
    "☀️ Get 15–20 minutes of sunlight daily for Vitamin D.",
    "🚭 Avoid smoking — it damages lungs and heart.",
    "🧼 Wash hands frequently to prevent infections.",
    "🏃 Regular exercise boosts immunity and mental health.",
    "🥗 Reduce processed food and sugar in your diet.",
    "📵 Limit screen time before bed for better sleep.",
    "🤝 Stay socially connected — it improves mental wellness.",
    "💊 Never self-medicate. Always consult a doctor.",
    "🩺 Get regular health checkups even when you feel fine.",
]

MEDICINES = {
    "Flu": ["Paracetamol (500mg)", "Cetirizine (antihistamine)", "Oseltamivir (Tamiflu) — prescription"],
    "Common Cold": ["Paracetamol", "Loratadine", "Saline nasal spray"],
    "COVID-19": ["Paracetamol for fever", "Vitamin C & D supplements", "Consult doctor immediately"],
    "Malaria": ["Consult doctor — antimalarial prescription required", "Paracetamol for fever"],
    "Dengue": ["Paracetamol only (NO aspirin/ibuprofen)", "ORS for hydration"],
    "Typhoid": ["Prescription antibiotics required", "ORS", "Paracetamol"],
    "Pneumonia": ["Prescription antibiotics required", "Paracetamol", "Bronchodilators if prescribed"],
    "Asthma": ["Prescribed inhaler (Salbutamol)", "Montelukast — prescription"],
    "Diabetes": ["Metformin — prescription only", "Monitor blood sugar daily"],
    "Hypertension": ["Amlodipine — prescription", "Reduce salt", "Regular monitoring"],
    "Gastroenteritis": ["ORS sachets", "Zinc supplements", "Probiotics"],
    "Migraine": ["Ibuprofen (400mg)", "Sumatriptan — prescription", "Rest in dark room"],
    "Anemia": ["Iron supplements (Ferrous sulfate)", "Vitamin B12", "Folic acid"],
    "Jaundice": ["No self-medication — consult hepatologist", "ORS", "Rest"],
    "Chickenpox": ["Calamine lotion", "Cetirizine for itching", "Paracetamol for fever"],
    "Urinary Tract Infection": ["Nitrofurantoin — prescription", "Drink lots of water", "Cranberry supplements"],
    "Sinusitis": ["Nasal decongestant spray", "Paracetamol", "Steam inhalation"],
    "Allergy": ["Cetirizine (10mg)", "Loratadine", "Fexofenadine"],
    "Arthritis": ["Ibuprofen (400mg)", "Diclofenac gel", "Glucosamine supplements"],
    "Depression": ["Consult psychiatrist — prescription required", "Vitamin D", "Omega-3"],
}

SEVERITY = {
    "Flu": "Moderate", "Common Cold": "Mild", "COVID-19": "High",
    "Malaria": "High", "Dengue": "High", "Typhoid": "High",
    "Pneumonia": "High", "Tuberculosis": "High", "Asthma": "Moderate",
    "Diabetes": "Chronic", "Hypertension": "Chronic", "Gastroenteritis": "Mild",
    "Migraine": "Moderate", "Anemia": "Moderate", "Jaundice": "High",
    "Chickenpox": "Moderate", "Measles": "High", "Arthritis": "Chronic",
    "Urinary Tract Infection": "Moderate", "Appendicitis": "Emergency",
    "Sinusitis": "Mild", "Allergy": "Mild", "Heart Disease": "Emergency",
    "Kidney Stones": "High", "Depression": "Moderate",
}

SYMPTOM_CATEGORIES = {
    "Head & Neurological": ["headache", "dizziness", "severe headache", "vision changes", "concentration problems", "loss of taste", "loss of smell"],
    "Respiratory": ["cough", "shortness of breath", "wheezing", "chest tightness", "breathlessness", "runny nose", "nasal congestion", "sneezing", "postnasal drip", "cough with blood", "persistent cough"],
    "Fever & General": ["fever", "mild fever", "chills", "fatigue", "weakness", "night sweats", "weight loss"],
    "Digestive": ["nausea", "vomiting", "diarrhea", "abdominal pain", "constipation", "loss of appetite", "abdominal tenderness", "dehydration"],
    "Skin & Eyes": ["rash", "itching", "blisters", "pale skin", "yellowing of skin", "yellowing of eyes", "red eyes", "mouth sores", "swelling"],
    "Pain & Body": ["muscle pain", "joint pain", "joint swelling", "stiffness", "chest pain", "back pain", "side pain", "eye pain", "pelvic pain", "sore throat", "facial pain"],
    "Urinary & Blood": ["frequent urination", "burning urination", "cloudy urine", "dark urine", "blood in urine", "increased thirst"],
    "Mental & Sleep": ["sadness", "sleep changes", "appetite changes", "loss of interest", "cold hands", "slow healing", "blurred vision"],
}

# ─── Database ──────────────────────────────────────────────────────────────────
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT, age INTEGER, blood_group TEXT, city TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, symptoms TEXT, predictions TEXT,
        checked_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, disease TEXT,
        UNIQUE(user_id, disease),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'username': row[1], 'name': row[3],
                'age': row[4], 'blood_group': row[5], 'city': row[6]}
    return None

def get_user_by_id(uid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id=?', (uid,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'username': row[1], 'name': row[3],
                'age': row[4], 'blood_group': row[5], 'city': row[6]}
    return None

def save_history(user_id, symptoms, predictions):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO history (user_id, symptoms, predictions, checked_at) VALUES (?,?,?,?)',
              (user_id, json.dumps(symptoms), json.dumps(predictions), datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()

def get_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT symptoms, predictions, checked_at FROM history WHERE user_id=? ORDER BY id DESC LIMIT 10', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{'symptoms': json.loads(r[0]), 'predictions': json.loads(r[1]), 'checked_at': r[2]} for r in rows]

def get_bookmarks(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT disease FROM bookmarks WHERE user_id=?', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]

# ─── Dataset ──────────────────────────────────────────────────────────────────
def load_diseases():
    diseases = []
    with open(DATASET_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            diseases.append(row)
    return diseases

def get_all_symptoms():
    diseases = load_diseases()
    symptoms = set()
    for disease in diseases:
        for i in range(1, 7):
            key = f'Symptom{i}'
            if key in disease and disease[key].strip():
                symptoms.add(disease[key].strip().lower())
    return sorted(list(symptoms))

def predict_disease(selected_symptoms):
    diseases = load_diseases()
    selected = [s.strip().lower() for s in selected_symptoms]
    results = []
    for disease in diseases:
        disease_symptoms = []
        for i in range(1, 7):
            key = f'Symptom{i}'
            if key in disease and disease[key].strip():
                disease_symptoms.append(disease[key].strip().lower())
        matched = [s for s in selected if s in disease_symptoms]
        if matched:
            match_score = len(matched) / max(len(disease_symptoms), len(selected))
            match_percent = round((len(matched) / len(disease_symptoms)) * 100)
            precautions = []
            for i in range(1, 5):
                key = f'Precaution{i}'
                if key in disease and disease[key].strip():
                    precautions.append(disease[key].strip())
            name = disease['Disease']
            results.append({
                'disease': name,
                'matched_symptoms': matched,
                'total_disease_symptoms': len(disease_symptoms),
                'match_score': match_score,
                'match_percent': match_percent,
                'precautions': precautions,
                'severity': SEVERITY.get(name, 'Unknown'),
                'medicines': MEDICINES.get(name, ['Consult a doctor for appropriate medication.']),
            })
    results.sort(key=lambda x: x['match_score'], reverse=True)
    return results[:3]

# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    tip = random.choice(HEALTH_TIPS)
    user = get_user_by_id(session.get('user_id')) if session.get('user_id') else None
    return render_template('home.html', tip=tip, user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        city = request.form.get('city', '').strip()
        if not username or not password:
            return render_template('register.html', error='Username and password are required.')
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password, name, age, blood_group, city) VALUES (?,?,?,?,?,?)',
                      (username, hash_password(password), name, age or None, blood_group, city))
            conn.commit()
            uid = c.lastrowid
            conn.close()
            session['user_id'] = uid
            session['username'] = username
            flash('Account created successfully! Welcome 🎉', 'success')
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username already taken. Try another.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username=? AND password=?', (username, hash_password(password)))
        row = c.fetchone()
        conn.close()
        if row:
            session['user_id'] = row[0]
            session['username'] = username
            flash(f'Welcome back, {username}! 👋', 'success')
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user = get_user_by_id(session['user_id'])
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        city = request.form.get('city', '').strip()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE users SET name=?, age=?, blood_group=?, city=? WHERE id=?',
                  (name, age or None, blood_group, city, session['user_id']))
        conn.commit()
        conn.close()
        flash('Profile updated! ✅', 'success')
        return redirect(url_for('profile'))
    history = get_history(session['user_id'])
    bookmarks = get_bookmarks(session['user_id'])
    return render_template('profile.html', user=user, history=history, bookmarks=bookmarks)

@app.route('/symptoms')
def symptoms():
    all_symptoms = get_all_symptoms()
    user = get_user_by_id(session.get('user_id')) if session.get('user_id') else None
    return render_template('symptoms.html', symptoms=all_symptoms,
                           categories=SYMPTOM_CATEGORIES, user=user)

@app.route('/predict', methods=['POST'])
def predict():
    selected_symptoms = request.form.getlist('symptoms')
    severity_level = request.form.get('severity', 'moderate')
    if not selected_symptoms:
        all_symptoms = get_all_symptoms()
        return render_template('symptoms.html', symptoms=all_symptoms,
                               categories=SYMPTOM_CATEGORIES,
                               error='Please select at least one symptom.',
                               user=get_user_by_id(session.get('user_id')) if session.get('user_id') else None)
    predictions = predict_disease(selected_symptoms)
    user = get_user_by_id(session.get('user_id')) if session.get('user_id') else None
    if session.get('user_id') and predictions:
        save_history(session['user_id'], selected_symptoms,
                     [{'disease': p['disease'], 'match_percent': p['match_percent']} for p in predictions])
    show_emergency = severity_level == 'severe' or (predictions and predictions[0].get('severity') in ['High', 'Emergency'])
    bookmarks = get_bookmarks(session['user_id']) if session.get('user_id') else []
    return render_template('result.html', predictions=predictions,
                           selected_symptoms=selected_symptoms,
                           severity_level=severity_level,
                           show_emergency=show_emergency,
                           user=user, bookmarks=bookmarks)

@app.route('/bookmark/<disease>', methods=['POST'])
def bookmark(disease):
    if not session.get('user_id'):
        return jsonify({'error': 'Login required'}), 401
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO bookmarks (user_id, disease) VALUES (?,?)', (session['user_id'], disease))
        conn.commit()
        action = 'added'
    except sqlite3.IntegrityError:
        c.execute('DELETE FROM bookmarks WHERE user_id=? AND disease=?', (session['user_id'], disease))
        conn.commit()
        action = 'removed'
    conn.close()
    return jsonify({'action': action})

@app.route('/bmi')
def bmi():
    user = get_user_by_id(session.get('user_id')) if session.get('user_id') else None
    return render_template('bmi.html', user=user)

@app.route('/hospitals')
def hospitals():
    user = get_user_by_id(session.get('user_id')) if session.get('user_id') else None
    city = request.args.get('city', user['city'] if user and user.get('city') else '')
    return render_template('hospitals.html', user=user, city=city)

@app.route('/appointment')
def appointment():
    user = get_user_by_id(session.get('user_id')) if session.get('user_id') else None
    return render_template('appointment.html', user=user)

@app.route('/about')
def about():
    user = get_user_by_id(session.get('user_id')) if session.get('user_id') else None
    return render_template('about.html', user=user)

@app.route('/api/symptoms')
def api_symptoms():
    return jsonify(get_all_symptoms())

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
