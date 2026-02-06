from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import boto3
import uuid
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = "photo_booking_secret"

# --- FIXED AWS CONFIG (N. Virginia) ---
# --- UPDATE THIS SECTION IN app_aws.py ---
REGION = "us-east-1"


dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1"
)
sns = aws_session.client("sns")
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:145023099836:aws_capstone_topic"

# DynamoDB Tables
clients_table = dynamodb.Table("Clients")
photographers_table = dynamodb.Table("Photographers")
bookings_table = dynamodb.Table("Bookings")

# --- PHOTOGRAPHER DATA (Moved up so routes can fetch it) ---
photographers_data = [
    {"name": "Elena Grace", "style": "Luxury", "vibe": "Guided (Posed)", "lighting": "Bright & Airy", "editing": "True to Color", "usage": "Magazine/Print", "setting": "Grand Architecture"},
    {"name": "Marcus Vane", "style": "Emotional", "vibe": "Candid (Natural)", "lighting": "Dark & Moody", "editing": "High Contrast", "usage": "Physical Album", "setting": "Urban/Cityscape"},
    {"name": "Sarah Zen", "style": "Artistic", "vibe": "Storytelling", "lighting": "Natural Light", "editing": "Film-like", "usage": "Instagram/Social", "setting": "Nature/Outdoor"},
    {"name": "Julian Cole", "style": "Minimalist", "vibe": "Editorial", "lighting": "Studio Flash", "editing": "Soft & Warm", "usage": "Professional Brand", "setting": "Private Studio"},
    {"name": "Leo Rivers", "style": "Vintage", "vibe": "Candid (Natural)", "lighting": "Natural Light", "editing": "Film-like", "usage": "Physical Album", "setting": "Nature/Outdoor"}
]

def send_notification(subject, message):
    try:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)
    except ClientError as e:
        print("SNS Error:", e)

# --- ROUTES ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        clients_table.put_item(Item={"email": email, "password": password})
        send_notification("New Client", f"{email} signed up.")
        return redirect(url_for("login"))
    return render_template("signup.html")

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

@app.route("/dashboard")
def dashboard():
    if "client" not in session: return redirect(url_for("login"))
    res = bookings_table.scan()
    user_bookings = [b for b in res.get("Items", []) if b["client_email"] == session["client"]]
    return render_template("dashboard.html", bookings=user_bookings)

@app.route("/services")
def services():
    return render_template("services.html")

@app.route('/recent-work')
def recent_work():
    return render_template('recent-work.html')

@app.route('/vows-in-veritas')
def vows_in_veritas():
    return render_template('view-gallery.html')

@app.route('/aura-reveal')
def aura_reveal():
    return render_template('aura-reveal.html')


@app.route('/dna-match')
def dna_match():  
    return render_template('dna_match.html', photographers=photographers_data)

@app.route('/calculate-match', methods=['POST'])
def calculate_match():
    user_dna = request.json
    results = []
    points = 100 / 6 
    for p in photographers_data:
        score = sum(1 for key in ['style', 'vibe', 'lighting', 'editing', 'usage', 'setting'] if p[key] == user_dna.get(key)) * points
        results.append({"name": p['name'], "match": round(score), "reason": f"Specialist in {p['style']}."})
    return jsonify(sorted(results, key=lambda x: x['match'], reverse=True)[:3])

@app.route('/portfolio/<name>')
def view_portfolio(name):
    photographer = next((p for p in photographers_data if p['name'] == name), None)
    if photographer:
        return render_template('portfolio_detail.html', photographer=photographers_data)
    return redirect(url_for('index'))

@app.route("/view")
def view():
    # RECTIFIED: Fetches from AWS instead of local DB
    res = bookings_table.scan()
    return render_template("view.html", bookings=res.get("Items", []))

# Add remaining basic routes for pages
@app.route('/prices')
def prices(): return render_template('prices.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

@app.route('/booking')
def booking():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('booking.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Generate a unique ID for this booking
        b_id = str(uuid.uuid4())
        
        # This saves (derives) the data to the Cloud
        bookings_table.put_item(Item={
            "booking_id": b_id, # Must match your DynamoDB Partition Key
            "client_name": request.form.get("client_name"),
            "event_date": request.form.get("event_date"),
            "service": request.form.get("service_type")
        })
        
        return render_template("booking_success.html")
        
    except ClientError as e:
        # This will show you if the token is the problem
        return f"Database Error: {e.response['Error']['Message']}"

def view():
    try:
        # Derived from your bookings_table object
        response = bookings_table.scan() 
        data = response.get("Items", [])
        return render_template("view.html", bookings=data)
    except Exception as e:
        # This will tell you if the 'fetch' failed due to keys
        return f"Database Fetch Error: {str(e)}"
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)

