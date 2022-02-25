import os

from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!!! Hi."


@app.route("/hello")
def hello():
    token = request.args.get("token")
    true_token = os.getenv("SECRET_TOKEN")

    if token == true_token:
        return f"Correct token {token}"
    else:
        return f"Incorrect token {token}"
