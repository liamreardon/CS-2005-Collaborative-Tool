# --- Imports ---
from flask import render_template, session, redirect, url_for, request
import os
# --- Custom imports ---
from app import app
from app.models import *


@app.route('/')
def index():
    return render_template("index.html", title="Example Title", text="Hello: World")

