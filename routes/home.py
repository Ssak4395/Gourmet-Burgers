from flask import Blueprint, render_template

site = Blueprint(__name__, __name__)

@site.route('/')
def viewHome():
   return render_template('home.html')