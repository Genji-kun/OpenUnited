from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/oudb?charset=utf8mb4' % quote('Abc123@')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = '4567890sdfghjklcvbnvb4567fg6yug'

app.config['CART_KEY'] = 'cart'
app.config['DATE_KEY'] = 'date'
app.config['ORDERER_KEY'] = 'orderer'
app.config['DETAILS_KEY'] = 'details'

app.config['S_INFO_KEY'] = 'info'
app.config['S_DETAILS_KEY'] = 's_details'

db = SQLAlchemy(app=app)
login = LoginManager(app=app)

