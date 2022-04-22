from flask import (
                Flask,
                flash, 
                render_template,
                session,
                redirect,
                url_for,
                request
                )
import requests
import json
from passlib.hash import pbkdf2_sha256
from forms import LoginForm, RegistrationForm
from functools import wraps

app = Flask(__name__)

urlDatabase = "http://127.0.0.1:5000"
urlWebsite = "http://127.0.0.1:5001"

# set the secret key for forms
app.config['SECRET_KEY'] = 'caed12f0f9063bf94fef30f10eaf5cbe'


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first", 'danger')
            return redirect(url_for('login'))
    return wrap

# login routes
@app.route("/", methods=['POST', 'GET'])
@app.route("/login", methods=['POST', 'GET'])
def login():

    if 'username' in session:
        flash(f"Already logged in as {session['username']}!", "success")
        return redirect(url_for('home'))

    form = LoginForm()

    # main validation (entered data into fields, correct email, etc.)
    if form.validate_on_submit():
        user_from_email_request = requests.get(urlDatabase + "/getuserfromemail/" + str(form.email.data))

        if (user_from_email_request.status_code == 200): # check if email in database
            user_data = user_from_email_request.json()

            # Now check password - does form password equal database password?
            if (pbkdf2_sha256.verify(form.password.data, user_data['password'])):
                session['username'] = user_data['First Name']
                flash(f"Welcome, {session['username']}!", "success")
                return redirect(url_for('home'))

            flash(f"Wrong Password!", "danger")
        else:
            flash(f"Email isn't in the database!", "danger")

    return render_template('login.html', title='login', form=form)

# register route
@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegistrationForm()

    # main validation (entered data into fields, correct email, etc.)
    if form.validate_on_submit():
        # make sure account doesn't already exist
        user_from_email_request = requests.get(urlDatabase + '/getuserfromemail/' + form.email.data)

        if (user_from_email_request.status_code == 404): # no user in database
            # create user
            create_request = requests.post(
                urlDatabase + '/createnewuser/' +
                str(form.first_name.data) + '/' +
                str(form.last_name.data) + '/' +
                str(form.email.data) + '/'
            )
            flash("User successfully created", "success")
            return redirect(url_for('home'))
        
        flash("Account already exists with that email!", "danger")
    
    return render_template('register.html', title='login', form=form)

# calendar route
@app.route("/calendar")
def calendar():
    return render_template('calendar.html')

# home route
@app.route("/home", methods=['GET','POST'])
@login_required
def home():
    return render_template('home.html', title='home')

@app.route("/otherHome")
def otherHome():
    return render_template('otherHome.html')

# logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/search_shift', methods=['GET', 'POST'])
def search_shift():
    if request.method == 'POST':
        date = request.form.get("date")
        time = request.form.get("time")
        position = request.form.get("position")
        ename = request.form.get("name")

        print(date, time, position, ename)
    
    print("searching shift!")
    return render_template('calendar.html')

# can run the application via command 'python3 app.py'
if __name__ == '__main__':
    app.run(port=5001, debug=True)