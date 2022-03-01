import os

import pandas as pd
from flask import Flask
from flask import request

from notion_connection import NotionConnection

app = Flask(__name__)
nc = NotionConnection()


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


@app.route("/now")
def now():
    token = request.args.get("token")
    true_token = os.getenv("SECRET_TOKEN")

    if token != true_token:
        return f"Incorrect token {token}"

    title = request.args.get("title")
    time_str = pd.Timestamp.now(tz='America/Los_Angeles').isoformat()

    assert title is not None

    nc.add(title, time_str)

    page_str = f"<p>Added {title}: {time_str} </p>\n"
    page_str += f"<p>Current contents:</p>"

    for row in nc.get_table():
        page_str += f"<p>{row}</p>\n"

    return page_str

