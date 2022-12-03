from enum import unique
from flask import Flask, render_template, flash, request, redirect, url_for, send_file, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Create a Flask Instance
app = Flask(__name__)
# Add Database
# Old SQLite DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MySQL DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/our_users'
# Secret Key!
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
#app.config['UPLOAD_FOLDER'] ="/home/oysch/mysite/uploads/"
app.config['MAX_CONTENT_LENGTH'] = 16 *1024 *1024 #16mb
app.config['ALLOWED_EXTENSIONS'] = ['.gpx', 'jpg']
# Initialize The Database
db = SQLAlchemy(app)

# Create Model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	fornavn = db.Column(db.String(30), nullable=False)
	etternavn = db.Column(db.String(30), nullable=False)
	ansattnr = db.Column(db.String(10), nullable=False, unique=True)
	avdeling = db.Column(db.String(120), nullable=False)
	regnr1 = db.Column(db.String(30), nullable=False)
	bilmerke1 = db.Column(db.String(30), nullable=False)
	regnr2 = db.Column(db.String(30), nullable=False)
	bilmerke2 = db.Column(db.String(30), nullable=False)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	# Create A String
	def __repr__(self):
		return '<Name %r>' % self.name



# Create a Form Class
class UserForm(FlaskForm):
	fornavn = StringField("Fornavn", validators=[DataRequired()])
	etternavn = StringField("Etternavn", validators=[DataRequired()])
	ansattnr = StringField("Ansattnummer", validators=[DataRequired()])
	avdeling = StringField("Avdeling")
	regnr1 = StringField("Regnr 1", validators=[DataRequired()])
	bilmerke1 = StringField("Bilmerke 1", validators=[DataRequired()])
	regnr2 = StringField("Regnr 2")
	bilmerke2 = StringField("Bilmerke 2")
	submit = SubmitField("Registrer")
	submit1 = SubmitField("Oppdater")



@app.route('/', methods=['GET', 'POST'])
def index():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(ansattnr=form.ansattnr.data).first()
		if user:
			flash('Ansattnummer ligger allerede inne!', 'category2')
			our_users = Users.query.order_by(Users.etternavn)
			return render_template("index.html",
			form=form,
			name=name,
			our_users=our_users)



		if user is None:
			user = Users(
			fornavn=form.fornavn.data.title().lstrip(),
			etternavn=form.etternavn.data.title(),
			ansattnr=form.ansattnr.data.lstrip(),
			avdeling=form.avdeling.data.capitalize().lstrip(),
			regnr1=form.regnr1.data.replace(' ', '').upper(),
			bilmerke1=form.bilmerke1.data.lstrip(),
			regnr2=form.regnr2.data.replace(' ', '').upper().lstrip(),
			bilmerke2=form.bilmerke2.data.lstrip(),)
			db.session.add(user)
			db.session.commit()
		name = form.fornavn.data
		form.fornavn.data = ''
		form.etternavn.data = ''
		form.ansattnr.data = ''
		form.avdeling.data = ''
		form.regnr1.data = ''
		form.bilmerke1.data = ''
		form.regnr2.data = ''
		form.bilmerke2.data = ''
		flash('Lagt til!', 'category1')


	our_users = Users.query.order_by(Users.etternavn)
	return render_template("index.html",
		form=form,
		name=name,
		our_users=our_users,)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()

	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash('Slettet!', 'category2')
		return redirect('/')

	except:
		our_users = Users.query.order_by(Users.etternavn)
		flash('Det oppstod et problem med å slette brukeren!', 'category2')
		return render_template("index.html",
		form=form, name=name,our_users=our_users)



# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.fornavn = request.form['fornavn'].title().lstrip()
		name_to_update.etternavn = request.form['etternavn'].title().lstrip()
		name_to_update.ansattnr = request.form['ansattnr'].lstrip()
		name_to_update.avdeling = request.form['avdeling'].capitalize().lstrip()
		name_to_update.regnr1 = request.form['regnr1'].replace(' ', '').upper().lstrip()
		name_to_update.bilmerke1 = request.form['bilmerke1']
		name_to_update.regnr2 = request.form['regnr2'].replace(' ', '').upper().lstrip()
		name_to_update.bilmerke2 = request.form['bilmerke2'].lstrip()
		try:
			db.session.commit()
			name = form.fornavn.data
			form.fornavn.data = ''
			form.etternavn.data = ''
			form.ansattnr.data = ''
			form.avdeling.data = ''
			form.regnr1.data = ''
			form.bilmerke1.data = ''
			form.regnr2.data = ''
			form.avdeling.data = ''
			flash('Oppdatert!', 'category1')

			our_users = Users.query.order_by(Users.etternavn)
			return render_template("index.html",
				form=form,
				name=name,
				our_users=our_users)
		except:
			flash('Noe gikk galt!', 'category2')
			return render_template("update.html",
				form=form,
				name_to_update = name_to_update)
	else:
		return render_template("update.html",
				form=form,
				name_to_update = name_to_update,
				id = id)


# Create Custom Error Pages

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500