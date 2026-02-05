from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# --- DATABASE SETUP ---
def get_db():
    conn = sqlite3.connect("booking.db")
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

# Ensure the database table exists on startup
with app.app_context():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT,
        event_type TEXT,
        event_date TEXT,
        service TEXT,
        duration INTEGER
    )
    """)
    conn.commit()
    conn.close()

# --- PHOTOGRAPHER DATA ---
photographers = [
    {"name": "Elena Grace", "style": "Luxury", "vibe": "Guided (Posed)", "lighting": "Bright & Airy", "editing": "True to Color", "usage": "Magazine/Print", "setting": "Grand Architecture"},
    {"name": "Marcus Vane", "style": "Emotional", "vibe": "Candid (Natural)", "lighting": "Dark & Moody", "editing": "High Contrast", "usage": "Physical Album", "setting": "Urban/Cityscape"},
    {"name": "Sarah Zen", "style": "Artistic", "vibe": "Storytelling", "lighting": "Natural Light", "editing": "Film-like", "usage": "Instagram/Social", "setting": "Nature/Outdoor"},
    {"name": "Julian Cole", "style": "Minimalist", "vibe": "Editorial", "lighting": "Studio Flash", "editing": "Soft & Warm", "usage": "Professional Brand", "setting": "Private Studio"},
    {"name": "Leo Rivers", "style": "Vintage", "vibe": "Candid (Natural)", "lighting": "Natural Light", "editing": "Film-like", "usage": "Physical Album", "setting": "Nature/Outdoor"}
]

# --- MAIN NAVIGATION ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/prices')
def prices():
    return render_template('prices.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/recent-work')
def recent_work():
    return render_template('recent-work.html')

@app.route('/portfolio/<name>')
def view_portfolio(name):
    photographer = next((p for p in photographers if p['name'] == name), None)
    if photographer:
        return render_template('portfolio_detail.html', photographer=photographer)
    return redirect(url_for('index'))

# --- DNA MATCHING LOGIC ---
@app.route('/dna-match')
def dna_match():  
    return render_template('dna_match.html', photographers=photographers)


@app.route('/calculate-match', methods=['POST'])
def calculate_match():
    user_dna = request.json
    results = []
    points_per_match = 100 / 6 

    for p in photographers:
        score = 0
        if p['style'] == user_dna.get('style'): score += points_per_match
        if p['vibe'] == user_dna.get('vibe'): score += points_per_match
        if p['lighting'] == user_dna.get('lighting'): score += points_per_match
        if p['editing'] == user_dna.get('editing'): score += points_per_match
        if p['usage'] == user_dna.get('usage'): score += points_per_match
        if p['setting'] == user_dna.get('setting'): score += points_per_match
        
        results.append({
            "name": p['name'], 
            "match": round(score), 
            "reason": f"Specializes in {p['style']} aesthetics."
        })
    
    results = sorted(results, key=lambda x: x['match'], reverse=True)
    return jsonify(results[:3])

# --- AUTHENTICATION & BOOKING ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')

        if email:   # simple validation
            session['user'] = email
            return redirect(url_for('booking'))
        else:
            flash("Invalid login details", "danger")

    return render_template('login.html')


@app.route('/booking')
def booking():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('booking.html')


@app.route('/submit', methods=['POST'])
def submit():
    # Collect form data
    name = request.form.get("client_name")
    contact = request.form.get("contact_number")
    event_type = request.form.get("event_type")
    event_date = request.form.get("event_date")
    service = request.form.get("service_type")
    duration = request.form.get("duration")

    # Save to Database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO bookings (name, contact, event_type, event_date, service, duration)
    VALUES (?,?,?,?,?,?)
    """, (name, contact, event_type, event_date, service, duration))
    conn.commit()
    conn.close()

    # Pass the name to the success page for a personalized thank you
    return render_template("booking_success.html", name=name)


@app.route('/vows-in-veritas')
def vows_in_veritas():
    return render_template('view-gallery.html')

@app.route('/aura-reveal')
def aura_reveal():
    return render_template('aura-reveal.html')


@app.route("/view")
def view():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings")
    data = cursor.fetchall()
    conn.close()
    return render_template("view.html", bookings=data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


