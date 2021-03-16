#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright © 2016-2017, Okta, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import os
import re

from xid import XID
from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import flask


app = Flask(__name__)
app.config["SECRET_KEY"] = "aon0nas0dnfasdlfn"
database_url = os.getenv("DATABASE_URL", "sqlite:///test-users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
db = SQLAlchemy(app)
CORS(app, resources={r"/socket.io*": {"origins": "*"}})
socketio = SocketIO(app)

class ListResponse:
    def __init__(self, list, start_index=1, count=None, total_results=0):
        self.list = list
        self.start_index = start_index
        self.count = count
        self.total_results = total_results

    def to_scim_resource(self):
        rv = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": self.total_results,
            "startIndex": self.start_index,
            "Resources": [],
        }
        resources = []
        for item in self.list:
            resources.append(item.to_scim_resource())
        if self.count:
            rv["itemsPerPage"] = self.count
        rv["Resources"] = resources
        return rv


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True)
    active = db.Column(db.Boolean, default=False)
    userName = db.Column(db.String(250), unique=True, nullable=False, index=True)
    familyName = db.Column(db.String(250))
    middleName = db.Column(db.String(250))
    givenName = db.Column(db.String(250))

    def __init__(self, resource):
        self.update(resource)
        self.id = XID().string()

    def update(self, resource):
        for attribute in ["userName", "active"]:
            if attribute in resource:
                setattr(self, attribute, resource[attribute])
        for attribute in ["givenName", "middleName", "familyName"]:
            if attribute in resource["name"]:
                setattr(self, attribute, resource["name"][attribute])

    def to_scim_resource(self):
        rv = {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "id": self.id,
            "userName": self.userName,
            "name": {
                "familyName": self.familyName,
                "givenName": self.givenName,
                "middleName": self.middleName,
            },
            "active": self.active,
            "meta": {
                "resourceType": "User",
                "location": url_for("user_get", user_id=self.id, _external=True),
                # "created": "2010-01-23T04:56:22Z",
                # "lastModified": "2011-05-13T04:42:34Z",
            },
        }
        return rv


def scim_error(message, status_code=500):
    rv = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
        "detail": message,
        "status": str(status_code),
    }
    return flask.jsonify(rv), status_code


def send_to_browser(obj):
    socketio.emit("user", {"data": obj}, broadcast=True, namespace="/test")


def render_json(obj):
    rv = obj.to_scim_resource()
    send_to_browser(rv)
    return flask.jsonify(rv)


@socketio.on("connect", namespace="/test")
def test_connect():
    print("Client connected")
    for user in User.query.filter_by(active=True).all():
        emit("user", {"data": user.to_scim_resource()})


@socketio.on("disconnect", namespace="/test")
def test_disconnect():
    print("Client disconnected")


@app.route("/")
def hello():
    return render_template("base.html")


@app.route("/scim/v2/Users/<user_id>", methods=["GET"])
def user_get(user_id):
    try:
        user = User.query.filter_by(id=user_id).one()
    except:
        return scim_error("User not found", 404)
    return render_json(user)


@app.route("/scim/v2/Users", methods=["POST"])
def users_post():
    user_resource = request.get_json(force=True)
    user = User(user_resource)
    db.session.add(user)
    db.session.commit()
    rv = user.to_scim_resource()
    send_to_browser(rv)
    resp = flask.jsonify(rv)
    resp.headers["Location"] = url_for(
        "user_get", user_id=user.userName, _external=True
    )
    return resp, 201


@app.route("/scim/v2/Users/<user_id>", methods=["PUT"])
def users_put(user_id):
    user_resource = request.get_json(force=True)
    user = User.query.filter_by(id=user_id).one()
    user.update(user_resource)
    db.session.add(user)
    db.session.commit()
    return render_json(user)


@app.route("/scim/v2/Users/<user_id>", methods=["PATCH"])
def users_patch(user_id):
    patch_resource = request.get_json(force=True)
    for attribute in ["schemas", "Operations"]:
        if attribute not in patch_resource:
            message = "Payload must contain '{}' attribute.".format(attribute)
            return message, 400
    schema_patchop = "urn:ietf:params:scim:api:messages:2.0:PatchOp"
    if schema_patchop not in patch_resource["schemas"]:
        return "The 'schemas' type in this request is not supported.", 501
    user = User.query.filter_by(id=user_id).one()
    for operation in patch_resource["Operations"]:
        if "op" not in operation and operation["op"] != "replace":
            continue
        value = operation["value"]
        for key in value.keys():
            setattr(user, key, value[key])
    db.session.add(user)
    db.session.commit()
    return render_json(user)


@app.route("/scim/v2/Users", methods=["GET"])
def users_get():
    query = User.query
    request_filter = request.args.get("filter")
    match = None
    if request_filter:
        match = re.match('(\w+) eq "([^"]*)"', request_filter)
    if match:
        (search_key_name, search_value) = match.groups()
        search_key = getattr(User, search_key_name)
        query = query.filter(search_key == search_value)
    count = int(request.args.get("count", 100))
    start_index = int(request.args.get("startIndex", 1))
    if start_index < 1:
        start_index = 1
    start_index -= 1
    query = query.offset(start_index).limit(count)
    total_results = query.count()
    found = query.all()
    rv = ListResponse(
        found, start_index=start_index, count=count, total_results=total_results
    )
    return flask.jsonify(rv.to_scim_resource())


@app.route("/scim/v2/Groups", methods=["GET"])
def groups_get():
    rv = ListResponse([])
    return flask.jsonify(rv.to_scim_resource())


@app.route("/db", methods=["POST"])
def create_db():
    db.create_all()
    user = User(
        {
            "schemas": ["urn:scim:schemas:core:1.0"],
            "userName": "test.user@username.example.com",
            "nickName": "test.user",
            "name": {"givenName": "Test", "familyName": "User"},
            "displayName": "test-user",
            "active": True,
            "emails": [{"value": "example@email.example.com", "primary": True}],
            "tenant": "example-user"
        }
    )
    db.session.add(user)
    db.session.commit()
    return f"Created {user.userName}", 201


if __name__ == "__main__":
    try:
        User.query.one()
    except:
        db.create_all()
    # app.debug = True
    socketio.run(app)
