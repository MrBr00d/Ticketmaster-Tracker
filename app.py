from flask import Flask, request, session, redirect, render_template
import supabase
import configparser
import os
import logging
logging.basicConfig(
level=logging.DEBUG,  # Capture all levels of logs
format='%(asctime)s - %(levelname)s - %(message)s',  # Log format with timestamp
handlers=[
    logging.FileHandler("logfile_flask.log"),  # Log to a file
    logging.StreamHandler()              # Log to console
    ]
)
# Flask app setup
ini_file_path = os.path.join(os.path.dirname(__file__), "secrets.ini")
app = Flask(__name__)
#app.config['APPLICATION_ROOT'] = '/tmtracker'
config = configparser.ConfigParser()
config.read(ini_file_path)
api_key = config["CREDENTIALS"]["API_KEY"]
app.secret_key = config["CREDENTIALS"]["FLASK_KEY"]

# Supabase setup
SUPABASE_URL = config["CREDENTIALS"]["URL"]  # Replace with your Supabase URL
SUPABASE_KEY =  api_key # Replace with your Supabase API key
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    response = supabase_client.auth.get_user()
    if response:
        return f"""Welcome {session['user']['email']}! <a href='/logout'><input type='button' value='Logout' /></a> <br>
                Your ntfy room key is: {session['user']['id']} <br>
                For documentation please go to <a href='/docs'>the documentation page</a> for explanaition how the app works. <br>
                Please select the action you want to do:<br>
                <a href='/view'><input type='button' value='View concerts' /></a><a href='/add'><input type='button' value='Add concerts' /></a>"""
    else:
        return  """
                Welcome to the admin page for the ticketmaster tracker! Please either login or sign up. <br>
                <a href='/login'><input type='button' value='Login' /></a> | <a href='/signup'><input type='button' value='Sign Up' />
                """
        

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        response = supabase_client.auth.sign_up({"email": email, "password": password})
        session["user"] = {"id": response.user.id,"email": response.user.email}
        return redirect('/')
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        if response.session:
            session["user"] = {"id": response.user.id,"email": response.user.email, "id": response.user.id}
            return redirect("/")
        return response
    return render_template('login.html')

@app.route('/logout')
def logout():
    response = supabase_client.auth.sign_out()
    print(response)
    session.pop('user', None)
    return redirect('/')

@app.route('/view')
def table():
    response = supabase_client.auth.get_user()
    if response:
        # Query the database using Supabase
        response = supabase_client.table('trackers').select('*').execute()

        # Extract data from the response
        data = response.data  # This is a list of dictionaries

        return render_template('table.html', data=data)
    else:
        return redirect('login')

@app.route('/delete', methods=['POST'])
def delete_item():
    user_id = request.form.get('id')
    concert_id = request.form.get('concert')
    response = supabase_client.table('trackers').delete().eq('user_id', user_id).eq('concert_id', int(concert_id)).execute()

    return redirect('/view')

@app.route('/add')
def add():
    response = supabase_client.auth.get_user()
    if response:
        return render_template('add.html')
    else:
        return redirect('/login')
    
@app.route('/addconcert', methods=["POST"])
def add_concert():
    response = supabase_client.auth.get_user()
    if response:
        user_id = response.user.id
        concert_id = request.form.get('concert_id')
        concert_name = request.form.get('concert_name')
        response = supabase_client.table('trackers').insert({"user_id": user_id, "concert_id": concert_id, "concert_name": concert_name}).execute()
        return redirect('/view')
    else:
        return redirect('/login')

@app.route('/docs')
def docs():
    return render_template('docs.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
