import os
from collections import namedtuple
import string
import random
from types import SimpleNamespace
import logging

import pandas as pd
from flask import Flask, redirect, request, render_template, url_for
from flask_cors import cross_origin

from notion_connection import NotionConnection
from redis_connection import RedisConnection, RedisConnectionException
from toggl_connection import TogglConnection

app = Flask(
    __name__,
)
nc = NotionConnection()

rc = RedisConnection()


state = SimpleNamespace(sid_list=[])


class BadTokenException(Exception):
    pass


class DuplicateRequestException(Exception):
    pass


class RedirectException(Exception):
    def __init__(self, message, url):
        super().__init__(message)
        self.url = url


def check_token():
    token = request.args.get("token")
    true_token = os.getenv("SECRET_TOKEN")

    if token != true_token:
        raise BadTokenException(f"Incorrect token {token}")
    else:
        return True


def check_sid(caller):
    sid = request.args.get("sid")
    if sid is None:
        random_sid = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        raise RedirectException(
            "redirecting", url=url_for(caller, sid=random_sid, **request.args)
        )

    try:
        if rc.check_sid(sid):
            raise DuplicateRequestException()
        else:
            rc.add_sid(sid)
    except RedisConnectionException as e:  # fallback to local
        logging.warning("Could not connect to redis, falling back to local state")

        if sid in state.sid_list:
            raise DuplicateRequestException()
        else:
            state.sid_list.append(sid)
            state.sid_list = state.sid_list[-10:]

    return sid


def get_current_table_contents_str():
    page_str = f"<p>Current contents:</p>"

    page_str += f"<p>"
    for row in nc.get_table():
        page_str += f"{row}<br>\n"
    page_str += f"</p>"
    return page_str


@app.route("/")
def hello_world():
    groups = nc.get_table_groupby_date()
    return render_template("index.html", groups=groups)


@app.route("/hello")
def hello():
    sid = check_sid(caller="hello")

    page_str = f"sid: {sid}"
    page_str += get_current_table_contents_str()
    return page_str


@app.route("/now")
def now():
    check_sid(caller="now")
    check_token()

    title = request.args.get("title")
    time_str = pd.Timestamp.now(tz="America/Los_Angeles").isoformat()

    assert title is not None

    nc.add(title, time_str)

    Item = namedtuple("Item", "title time")
    new_item = Item(title=title, time=time_str[:19])

    groups = nc.get_table_groupby_date()

    return render_template("index.html", groups=groups, new_item=new_item)


@app.route("/toggl")
def toggl_start():
    check_token()

    tc = TogglConnection()

    title = request.args.get("title")
    project = request.args.get("project")

    current_timer = tc.get_current()
    if current_timer is not None:  # a timer is running
        if current_timer["description"] == title:  # activity is same
            tc.stop_current_timer()
            return render_template("timer.html", status="Stopped")
        else:  # activity is different
            tc.stop_current_timer()
            tc.start_timer(title, project)
    else:  # no timer running
        tc.start_timer(title, project)

    return render_template(
        "timer.html", status="Running", current_data=tc.get_current()
    )


@app.route("/nfc", methods=["GET", "POST"])
@cross_origin()
def nfc():
    if request.method == "GET":
        return render_template("nfc.html")
    elif request.method == "POST":
        print("data:", request.data)
        print("json:", request.json)

        tag_data = request.json
        print(f'tag_data: {tag_data}')

        return tag_data


@app.errorhandler(BadTokenException)
def handle_bad_token(e):
    return f"Bad token!\n{e}"


@app.errorhandler(RedirectException)
def handle_redirect(e):
    return redirect(e.url)


@app.errorhandler(DuplicateRequestException)
def handle_redirect(e):
    return f"Duplicate request! {e}"
