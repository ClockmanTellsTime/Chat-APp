from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import random
from bs4 import BeautifulSoup
from os import environ
from dotenv import load_dotenv
import requests
import pusher

load_dotenv()

password = "31h7143jdh8413jd3hd431h8d143dij87xdasg7f143"
URL = "https://sillysamlikesjam.pythonanywhere.com?password=" + password

deleted = False
admins = ["shaurya", "lilnasxbiggestfan","BBC"]

pusher_client = pusher.Pusher(
  app_id='1671920',
  key='3ee636d6edcdecffe90e',
  secret='b4805fbd535ae0d56573',
  cluster='us3',
  ssl=True
)

def openDB():
  with open("data.json", 'r') as f:
    data = json.load(f)

  return data


def writeDB(data):
  with open("data.json", 'w') as f:
    json.dump(data, f, indent=4)

  print("sent")


app = Flask(__name__)
app.config["SECRET_KEY"] = "432178i784321789hcer7fncsansdjfd8h3e9823he"

socketio = SocketIO(app, cors_allowed_origins="*")

db = openDB()


#Clear rooms in the thing
for user in db["userdata"]:
  db["userdata"][user]["rooms"] = []


def is_html(input_str):
  try:
    soup = BeautifulSoup(input_str, "html.parser")
    return any(soup.find_all(True))
  except:
    return False


@app.route("/", methods=["POST", "GET"])
def join():
  #return render_template("index.html")
  global deleted

  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  if deleted:
    return render_template("index.html")

  return render_template("chat.html")


@app.route("/createserver", methods=["POST", "GET"])
def createserver():
  user = session.get("user")
  if not user or user == "":
    return redirect(url_for("signin"))

  if request.method == "POST":
    name = request.form.get("name")

    letters = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "0",
        "_",
        " ",
    ]

    for i in str(name):
      if not i in letters:
        return render_template(
            "createserver.html",
            r=
            "You can only use letters a - z, digits 1 - 0,and _ in your group chat name",
        )

    if name.strip() == "":
      return render_template("createserver.html",
                             r="Your Groupchat must have a name...")

    if len(name) > 50:
      return render_template(
          "createserver.html",
          r="Your Groupchat must have be shorter than 50 characters!",
      )

    db["servers"]["servers"] += 1
    id = str(db["servers"]["servers"])

    db["servers"][id] = {"members": [user], "name": name, "owner": user}

    db["users"][user]["servers"].append(id)

    return redirect(url_for("join"))

  return render_template("createserver.html", r="")


@app.route("/sign-up", methods=["POST", "GET"])
def signup():
  user = session.get("user")

  if user and user != "":
    return redirect(url_for("join"))

  if request.method == "GET":
    return render_template("signup.html")

  elif request.method == "POST":
    usr = request.form.get("usr")
    password = request.form.get("pass")

    letters = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "0",
        "_",
    ]

    if usr == "":
      return render_template("signup.html", r="You must have a username...")

    if usr == len(usr) * usr[0] and usr[0] == "+":
      return render_template("signup.html", r="You must have a username...")

    if len(usr) > 20 or len(usr) < 3:
      return render_template(
          "signup.html", r="Your username must be between 3 and 20 characters")

    if password == "":
      return render_template("signup.html", r="You must have a password...")

    if password == len(password) * password[0] and password[0] == "+":
      return render_template("signup.html", r="You must have a password...")

    for i in str(usr):
      if not i in letters:
        return render_template(
            "signup.html",
            r=
            "You can only use letters a - z, digits 1 - 0,and _ in your username",
        )

    if usr in db["users"]:
      return render_template("signup.html", r="User already exists")

    if "server" in str(usr):
      return render_template(
          "signup.html", r="Username cannot contain the word 'server'! Sorry")

    # if valid
    else:
      db["users"][usr] = {
          "usr": usr,
          "password": password,
          "admin": False,
          "friendData": {
              "friends": [],
              "outgoing": [],
              "pending": [],
              "blocked": [],
              "blockedby": [],
          },
          "invincible": False,
          "servers": [],
          "banned": False,
      }

      session["user"] = usr

      session["id"] = usr + str(random.randint(1, 1000000000000000))
      return redirect(url_for("join"))

  return render_template("signup.html", r="")


@app.route("/sign-in", methods=["POST", "GET"])
def signin():
  user = session.get("user")

  if user and user != "":
    return redirect(url_for("join"))

  if request.method == "POST":
    usr = request.form.get("usr")
    password = request.form.get("pass")

    if usr == "":
      return render_template("signin.html", r="You must have a username...")

    if password == "":
      return render_template("signin.html", r="You must have a password...")

    if usr == len(usr) * usr[0] and usr[0] == "+":
      return render_template("signin.html", r="You must have a username...")

    if password == len(password) * password[0] and password[0] == "+":
      return render_template("signin.html", r="You must have a password...")

    if usr in db["users"].keys():
      if db["users"][usr]["banned"]:
        return render_template("banned.html", usr=usr)

      if db["users"][usr]["password"] == password:
        session["user"] = usr
        session["id"] = usr + str(random.randint(1, 1000000000000000))
        return redirect(url_for("join"))

      else:
        return render_template("signin.html",
                               r="Password and/or Username is incorrect!")
    else:
      return render_template("signin.html", r="User was not found")

  return render_template("signin.html", r="")


@app.route("/logout", methods=["POST", "GET"])
def logout():
  session["user"] = ""
  return redirect(url_for("signin"))


@app.route("/friends", methods=["POST", "GET"])
def friends():
  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  return render_template("friends.html")


@app.route("/configure/<id>/", methods=["POST", "GET"])
def configure(id):
  user = session.get("user")

  id = id

  if not user or user == "":
    return redirect(url_for("signin"))

  if request.method == "POST":
    id = request.form.get("id")
    action = request.form.get("type")

    print(id, action)

    memberstoupdate = []

    for i in db["servers"][id]["members"]:
      memberstoupdate.append(i)

    if not id in db["servers"].keys():
      return redirect(url_for("join"))

    if user == db["servers"][id]["owner"]:
      if action == "remove":
        name = request.form.get("name")

        if (name in db["servers"][id]["members"]
            and id in db["users"][name]["servers"]):
          db["servers"][id]["members"].remove(name)
          db["users"][name]["servers"].remove(id)

          db["chatData"]["server_" +
                         str(id)]["members"] = db["servers"][id]["members"]

        socketio.emit("reload", room=name)

      if action == "add":
        name = request.form.get("name")

        if (not name in db["servers"][id]["members"]
            and not id in db["users"][name]["servers"]
            and name in db["users"][user]["friendData"]["friends"]):
          db["servers"][id]["members"].append(name)
          db["users"][name]["servers"].append(id)

          db["chatData"]["server_" +
                         str(id)]["members"] = db["servers"][id]["members"]

          memberstoupdate.append(name)

      if action == "changename":
        name = request.form.get("name")

        if len(name) < 50:
          db["servers"][id]["name"] = name

      if action == "deleteserver":
        name = request.form.get("name")

        if name == "confirm":
          for member in db["servers"][id]["members"]:
            db["users"][member]["servers"].remove(id)

          print(id)

          del db["chatData"]["server_" + str(id)]

          del db["servers"][id]

      for member in memberstoupdate:
        serverData = {}

        servers = db["users"][member]["servers"]

        for server in servers:
          if server == "servers":
            continue

          serverData[server] = {
              "owner": db["servers"][str(server)]["owner"],
              "name": db["servers"][str(server)]["name"],
              "members": db["servers"][str(server)]["members"],
              "id": server,
          }

          data = {
              "members": db["servers"][server]["members"],
              "server": db["servers"][server]["name"],
              "owner": db["servers"][server]["owner"],
              "id": server,
          }

          if db["servers"][server]["name"] in db["users"][member].keys():
            socketio.emit("servermembers", data, room=member)

        socketio.emit("serverData", serverData, room=member)

  if str(id) in db["servers"].keys():
    if user == db["servers"][str(id)]["owner"]:
      return render_template("configure.html",
                             server=db["servers"][str(id)]["name"],
                             id=id)

    else:
      return "You dont have permission to do this!"

  else:
    return redirect(url_for("join"))


@app.route("/leave/<id>", methods=["POST", "GET"])
def leave(id):
  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  if user in db["servers"][id]["members"] and id in db["users"][user][
      "servers"]:
    db["servers"][id]["members"].remove(user)
    db["users"][user]["servers"].remove(id)

    db["chatData"]["server_" +
                   str(id)]["members"] = db["servers"][id]["members"]

  for member in db["servers"][id]["members"]:
    data = {
        "members": db["servers"][id]["members"],
        "server": db["servers"][id]["name"],
        "owner": db["servers"][id]["owner"],
        "id": id,
    }

    socketio.emit("servermembers", data, room=member)

  return redirect(url_for("join"))


@app.route("/reloadall", methods=["POST", "GET"])
def admin_1():
  user = session.get("user")

  if user in admins:
    socketio.emit("reload")
    return "reloading..."

  return "404 page not found"


@app.route("/logoutall", methods=["POST", "GET"])
def admin_2():
  user = session.get("user")
  user_to_logout = request.args.get("user")

  if user in admins:
    if not user_to_logout:
      socketio.emit("logout")
      return "logging everyone out..."

    else:
      socketio.emit("logout", room=user_to_logout)
      return "logging " + user_to_logout + " out..."

  return "404 page not found"


@app.route("/ban", methods=["POST", "GET"])
def admin_3():
  user = session.get("user")
  user_to_ban = request.args.get("user")

  if user in admins:

    db["users"][user_to_ban]["banned"] = True

    socketio.emit("logout", room=user_to_ban)

    return "banning " + user_to_ban

  return "404 page not found"


@app.route("/unban", methods=["POST", "GET"])
def admin_4():
  user = session.get("user")
  user_to_ban = request.args.get("user")

  if user in admins:
    db["users"][user_to_ban]["banned"] = False

    return "unbanning " + user_to_ban

  return "404 page not found"


@app.route("/loginasuser", methods=["POST", "GET"])
def admin_5():
  user = session.get("user")
  user_to_hack = request.args.get("user")

  if user in admins:
    session["user"] = user_to_hack
    return "logging in as " + user_to_hack

  return "404 page not found"


@app.route("/resetchat", methods=["POST", "GET"])
def admin_6():
  user = session.get("user")

  if user in admins:
    db["chatData"]["global"] = {"messages": {}, "ids": 0, "type": "global"}

    socketio.emit("reload")
    return "Clearing chat"

  return "404 page not found"


@app.route("/delete", methods=["POST", "GET"])
def admin_7():
  global deleted

  user = session.get("user")

  if user in admins:
    deleted = True
    socketio.emit("reload")
    return "deleting..."

  return "404 page not found"


@app.route("/undelete", methods=["POST", "GET"])
def admin_8():
  global deleted

  user = session.get("user")

  if user in admins:
    deleted = False
    socketio.emit("reload")
    return "undeleting..."

  return "404 page not found"


@socketio.on("message")
def handle_message(message, time):
  user = session.get("user")
  room = session.get("room")
  id = session.get("id")

  if not user or user == "":
    return False

  if not room:
    return False

  if message == "":
    return

  if is_html(message):
    return

  if len(message) > 1000:
    return

  if not room in db["chatData"]:
    db["chatData"][room] = {"messages": {}, "ids": 0}

  db["chatData"][room]["ids"] += 1

  id = str(db["chatData"][room]["ids"])

  db["chatData"][room]["messages"][id] = {
      "message": message,
      "time": time,
      "user": user
  }

  data = {
      "message": message,
      "room": room,
      "time": time,
      "user": user,
      "type": db["chatData"][room]["type"]
  }

  if "server_" in str(room):
    data["servername"] = db["servers"][room[7:len(room)]]["name"]

  emit(
      "message",
      data,
      room=room,
  )

  if db["chatData"][room]["type"] == "dm":
    otherUser = ""

    for i in db["chatData"][room]["members"]:
      if i == user:
        continue
      else:
        otherUser = i

    # update messages read when they are in channel

    if user not in db["userdata"].keys():
      db["userdata"][user] = {}

    if not room in db["userdata"][user].keys():
      db["userdata"][user][room] = {"read": 0}

    if otherUser not in db["userdata"].keys():
      db["userdata"][otherUser] = {"rooms": []}

    if not room in db["userdata"][otherUser].keys():
      db["userdata"][otherUser][room] = {"read": 0}

    if otherUser in db["userdata"].keys():
      if room in db["userdata"][otherUser]["rooms"]:
        db["userdata"][otherUser][room]["read"] = int(
            db["chatData"][room]["ids"])

      else:
        emit(
            "dm",
            {
                "amount":
                int(db["chatData"][room]["ids"]) -
                db["userdata"][otherUser][room]["read"],
                "room":
                room,
                "user":
                user,
            },
            room=otherUser,
        )
        emit(
            "dm2",
            {
                "amount":
                int(db["chatData"][room]["ids"]) -
                db["userdata"][otherUser][room]["read"],
                "room":
                room,
                "user":
                user,
            },
            room=otherUser,
        )

    # update our users read as well
    db["userdata"][user][room]["read"] = int(db["chatData"][room]["ids"])


@socketio.on("joinroom")
def joinRoom(room):
  user = session.get("user")
  id = session.get("id")
  room2 = session.get("room")

  if not user or user == "":
    return redirect(url_for("signin"))

  if not user in db["userdata"].keys():
    db["userdata"][user] = {}

  if not "rooms" in db["userdata"][user].keys():
    db["userdata"][user]["rooms"] = []

  # if they already in a room
  if room2:
    leave_room(room2)

    if room2 in db["userdata"][user]["rooms"]:
      db["userdata"][user]["rooms"].remove(room2)

  if not room in db["chatData"]:

    for server in db["servers"]:
      if server == "servers":
        continue

      id = room[7:len(room)]

      if str(id) in db["servers"]:
        db["chatData"][room] = {
            "messages": {},
            "ids": 0,
            "type": "groupchat",
            "members": db["servers"][server]["members"],
        }
      else:
        socketio.emit("allmessages",
                      db["chatData"]["global"]["messages"],
                      room=id)
        session["room"] = "global"
        join_room("global")

        db["userdata"][user]["rooms"].append("global")

  if room != "global":
    if user in db["chatData"][room]["members"]:
      socketio.emit("allmessages", db["chatData"][room]["messages"], room=id)
      session["room"] = room
      join_room(room)

      db["userdata"][user]["rooms"].append(room)

    else:
      socketio.emit("allmessages",
                    db["chatData"]["global"]["messages"],
                    room=id)
      session["room"] = "global"
      join_room("global")

      db["userdata"][user]["rooms"].append("global")

  else:
    socketio.emit("allmessages", db["chatData"]["global"]["messages"], room=id)
    session["room"] = "global"
    join_room("global")

    db["userdata"][user]["rooms"].append("global")


@socketio.on("joindm")
def joinDm(otherUser):
  user = session.get("user")
  id = session.get("id")
  room2 = session.get("room")

  if not user or user == "":
    return redirect(url_for("signin"))

  if not user in db["userdata"].keys():
    db["userdata"][user] = {}

  if not "rooms" in db["userdata"][user].keys():
    db["userdata"][user]["rooms"] = []

  if room2:
    leave_room(room2)

    if room2 in db["userdata"][user]["rooms"]:
      db["userdata"][user]["rooms"].remove(room2)

  room1 = user + "TO" + otherUser
  room2 = otherUser + "TO" + user

  if (otherUser in db["users"][user]["friendData"]["friends"]
      and user in db["users"][otherUser]["friendData"]["friends"]):
    if room1 in db["chatData"]:
      session["room"] = room1
      join_room(room1)
      socketio.emit("allmessages", db["chatData"][room1]["messages"], room=id)

      if not user in db["userdata"].keys():
        db["userdata"][user] = {}

      if not room1 in db["userdata"][user].keys():
        db["userdata"][user][room1] = {"read": 0}

      db["userdata"][user][room1]["read"] = int(db["chatData"][room1]["ids"])

      db["userdata"][user]["rooms"].append(room1)

    elif room2 in db["chatData"]:
      session["room"] = room2
      join_room(room2)
      socketio.emit("allmessages", db["chatData"][room2]["messages"], room=id)

      if not user in db["userdata"].keys():
        db["userdata"][user] = {}

      if not room2 in db["userdata"][user].keys():
        db["userdata"][user][room2] = {"read": 0}

      db["userdata"][user][room2]["read"] = int(db["chatData"][room2]["ids"])

      db["userdata"][user]["rooms"].append(room2)

    else:
      db["chatData"][room1] = {
          "messages": {},
          "ids": 0,
          "members": [user, otherUser],
          "type": "dm",
      }
      join_room(room1)
      session["room"] = room1
      socketio.emit("allmessages", db["chatData"][room1]["messages"], room=id)

      db["userdata"][user]["rooms"].append(room1)

  else:
    socketio.emit("allmessages", db["chatData"]["global"]["messages"], room=id)
    session["room"] = "global"
    join_room("global")

    db["userdata"][user]["rooms"].append("global")


@socketio.on("getfrienddata")
def frienddata():
  user = session.get("user")
  id = session.get("id")

  if not user or user == "":
    return redirect(url_for("signin"))

  socketio.emit("frienddata", db["users"][user]["friendData"], room=id)

  # get amount of notifications from dm they have for each friend

  for friend in db["users"][user]["friendData"]["friends"]:
    room1 = user + "TO" + friend
    room2 = friend + "TO" + user

    if not user in db["userdata"].keys():
      db["userdata"][user] = {}

    if room1 in db["chatData"]:
      if not room1 in db["userdata"][user].keys():
        db["userdata"][user][room1] = {"read": 0}

      emit(
          "dm",
          {
              "amount":
              int(db["chatData"][room1]["ids"]) -
              db["userdata"][user][room1]["read"],
              "room":
              room1,
              "user":
              friend,
          },
          room=user,
      )

    elif room2 in db["chatData"]:
      if room2 in db["chatData"]:
        if not room2 in db["userdata"][user].keys():
          db["userdata"][user][room2] = {"read": 0}

      emit(
          "dm",
          {
              "amount":
              int(db["chatData"][room2]["ids"]) -
              db["userdata"][user][room2]["read"],
              "room":
              room2,
              "user":
              friend,
          },
          room=user,
      )


@socketio.on("logout")
def logout():
  user = session.get("user")

  if not user:
    return

  leave_room(user)


@socketio.on("connect")
def connect():
  user = session.get("user")
  id = session.get("id")

  if user and user != "":
    join_room(user)

  if id and id != "":
    join_room(id)


@socketio.on("disconnect")
def disconnect():
  user = session.get("user")
  id = session.get("id")
  room = session.get("room")

  if not user or user == "":
    return

  if not user in db["userdata"].keys():
    db["userdata"][user] = {}

  if not "rooms" in db["userdata"][user].keys():
    db["userdata"][user]["rooms"] = []

  if room:
    leave_room(room)

    if room in db["userdata"][user]["rooms"]:
      db["userdata"][user]["rooms"].remove(room)


@socketio.on("sendfriendrequest")
def friendrequest(friend):
  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  if str(friend).strip() == "":
    return

  if (user != friend
      and friend not in db["users"][user]["friendData"]["friends"]
      and user not in db["users"][friend]["friendData"]["friends"]
      and friend not in db["users"][user]["friendData"]["blocked"]
      and user not in db["users"][friend]["friendData"]["blockedby"]
      and not friend in db["users"][user]["friendData"]["outgoing"]
      and not friend in db["users"][user]["friendData"]["pending"]):
    db["users"][user]["friendData"]["outgoing"].append(friend)
    db["users"][friend]["friendData"]["pending"].append(user)

    socketio.emit("frienddata", db["users"][user]["friendData"], room=user)
    socketio.emit("frienddata", db["users"][friend]["friendData"], room=friend)


@socketio.on("blockuser")
def blockuser(friend):
  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  if str(friend).strip() == "":
    return

  if (user != friend and friend in db["users"] and user in db["users"]
      and not friend in db["users"][user]["friendData"]["blocked"]
      and not user in db["users"][friend]["friendData"]["blockedby"]):
    db["users"][user]["friendData"]["blocked"].append(friend)
    db["users"][friend]["friendData"]["blockedby"].append(user)

    if friend in db["users"][user]["friendData"]["pending"]:
      db["users"][user]["friendData"]["pending"].remove(friend)

    if friend in db["users"][user]["friendData"]["outgoing"]:
      db["users"][user]["friendData"]["outgoing"].remove(friend)

    if friend in db["users"][user]["friendData"]["friends"]:
      db["users"][user]["friendData"]["friends"].remove(friend)

    if user in db["users"][friend]["friendData"]["pending"]:
      db["users"][friend]["friendData"]["pending"].remove(user)

    if user in db["users"][friend]["friendData"]["outgoing"]:
      db["users"][friend]["friendData"]["outgoing"].remove(user)

    if user in db["users"][friend]["friendData"]["friends"]:
      db["users"][friend]["friendData"]["friends"].remove(user)

    socketio.emit("frienddata", db["users"][user]["friendData"], room=user)
    socketio.emit("frienddata", db["users"][friend]["friendData"], room=friend)


@socketio.on("removefriend")
def removefriend(friend):
  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  if user != friend and user in db["users"] and friend in db["users"]:
    db["users"][user]["friendData"]["friends"].remove(friend)
    db["users"][friend]["friendData"]["friends"].remove(user)

    socketio.emit("frienddata", db["users"][user]["friendData"], room=user)
    socketio.emit("frienddata", db["users"][friend]["friendData"], room=friend)


@socketio.on("unblockuser")
def unblockuser(friend):
  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  if (user != friend and friend in db["users"] and user in db["users"]
      and friend in db["users"][user]["friendData"]["blocked"]
      and user in db["users"][friend]["friendData"]["blockedby"]):
    db["users"][user]["friendData"]["blocked"].remove(friend)
    db["users"][friend]["friendData"]["blockedby"].remove(user)

    socketio.emit("frienddata", db["users"][user]["friendData"], room=user)
    socketio.emit("frienddata", db["users"][friend]["friendData"], room=friend)


@socketio.on("cancelfriendrequest")
def cancelfriendrequest(friend):
  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  if (friend in db["users"][user]["friendData"]["outgoing"]
      and user in db["users"][friend]["friendData"]["pending"]):
    db["users"][user]["friendData"]["outgoing"].remove(friend)
    db["users"][friend]["friendData"]["pending"].remove(user)

    socketio.emit("frienddata", db["users"][user]["friendData"], room=user)
    socketio.emit("frienddata", db["users"][friend]["friendData"], room=friend)


@socketio.on("acceptfriendrequest")
def acceptfriendrequest(friend):
  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  if (friend in db["users"][user]["friendData"]["pending"]
      and user in db["users"][friend]["friendData"]["outgoing"]):
    db["users"][user]["friendData"]["friends"].append(friend)
    db["users"][friend]["friendData"]["friends"].append(user)

    db["users"][user]["friendData"]["pending"].remove(friend)
    db["users"][friend]["friendData"]["outgoing"].remove(user)

    socketio.emit("frienddata", db["users"][user]["friendData"], room=user)
    socketio.emit("frienddata", db["users"][friend]["friendData"], room=friend)


@socketio.on("declinefriendrequest")
def declinefriendrequest(friend):
  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  if (friend in db["users"][user]["friendData"]["pending"]
      and user in db["users"][friend]["friendData"]["outgoing"]):
    db["users"][user]["friendData"]["pending"].remove(friend)
    db["users"][friend]["friendData"]["outgoing"].remove(user)

    socketio.emit("frienddata", db["users"][user]["friendData"], room=user)
    socketio.emit("frienddata", db["users"][friend]["friendData"], room=friend)


@socketio.on("getservers")
def getServers():
  user = session.get("user")
  id = session.get("id")

  if not user or user == "":
    return

  servers = db["users"][user]["servers"]

  serverData = {}

  for server in servers:
    serverData[server] = {
        "owner": db["servers"][str(server)]["owner"],
        "name": db["servers"][str(server)]["name"],
        "members": db["servers"][str(server)]["members"],
        "id": server,
    }

  socketio.emit("serverData", serverData, room=id)


@app.route("/connect",methods=["POST","GET"])
def connect():
    data = request.json
    event_type = data.get('event_type', '')
    socketid = data.get('socketId', '')
    url = data.get("url","")

    # You can also trigger an event back to the client if needed
    pusher_client.trigger(session.get("id"), 'server-to-client', {'message': 'Data received on the server'})

    return "yes"


def authenticate_channel(name,id):
    return True

@app.route('/pusher/auth', methods=['POST'])
def pusher_auth():
    channel_name = request.form['channel_name']
    socket_id = request.form['socket_id']

    if authenticate_channel(channel_name, socket_id):
        response = pusher_client.authenticate(
            channel=channel_name,
            socket_id=socket_id
        )
        return jsonify(response)
    else:
        return jsonify(response), 403  # Access forbidden


def get_usernames(string):
    # Split the string by '2'
    parts = string.split('2')
    
    # Check if there are at least two parts separated by '2'
    if len(parts) >= 2:
        username1 = parts[0][len('private-'):]  # Extract the first username
        username2 = parts[1]  # Extract the second username
        return username1, username2
    else:
        return None, None  # Return None if the string format doesn't match


@app.route('/get-messages', methods=['POST'])
def get_messages():
    data = request.json
    room = data.get('room', '')
    socket_id = data.get("socket_id","")

    user = session.get("user")


    session["room"] = room
    
    print(room, socket_id, user,"d")


    if not room in db["chatData"]:

        if "server" in str(room):
            for server in db["servers"]:
                if server == "servers":
                    continue

                id = room[15:len(room)]


                if str(id) in db["servers"]:
                    db["chatData"][room] = {
                        "messages": {},
                        "ids": 0,
                        "type": "groupchat",
                        "members": db["servers"][server]["members"],
                    }
        else:
            db["chatData"][room] = {
                "messages": {},
                "ids": 0,
                "type": "dm",
                "members": get_usernames(room),
            }



    pusher_client.trigger(socket_id,"messages",db["chatData"][room]["messages"])

    return "d"

@app.route('/get-friends', methods=['POST'])
def get_friends():
    data = request.json
    socket_id = data.get("socket_id","")
    user = session.get("user")

    pusher_client.trigger(socket_id,"friends",db["users"][user]["friendData"])
    return "d"

@app.route('/get-server-members', methods=['POST'])
def get_server_members():
    data = request.json
    user = session.get("user")
    id = session.get("id")
    server = data.get("server_id","")
    socket_id = data.get("socket_id","")

    if not user or user == "":
        return

    servers = db["servers"]

    if server in servers.keys():
        if user in servers[server]["members"]:
            members = servers[server]["members"]

        data = {
            "members": members,
            "server": servers[server]["name"],
            "owner": servers[server]["owner"],
            "id": server,
        }

        pusher_client.trigger(socket_id,"servermembers",data)
    return "e"



@app.route('/get-servers', methods=['POST'])
def get_servers():
    data = request.json
    socket_id = data.get("socket_id","")
    user = session.get("user")

    servers = db["users"][user]["servers"]

    serverData = {}

    for server in servers:
        serverData[server] = {
            "owner": db["servers"][str(server)]["owner"],
            "name": db["servers"][str(server)]["name"],
            "members": db["servers"][str(server)]["members"],
            "id": server,
        }


    pusher_client.trigger(socket_id,"servers",serverData)
    return "d"



@app.route('/message', methods=['POST'])
def message():
    data = request.json
    socket_id = data.get("socket_id","")
    user = session.get("user")
    room = session.get("room")
    message = data.get("message","")
    time = data.get("time","")

    print(room,"fdsafdsafasd")

    if not user or user == "":
        return False

    if not room:
        return False

    if message == "":
        return

    if is_html(message):
        return

    if len(message) > 1000:
        return

    if not room in db["chatData"]:
        db["chatData"][room] = {"messages": {}, "ids": 0}

    db["chatData"][room]["ids"] += 1

    id = str(db["chatData"][room]["ids"])

    db["chatData"][room]["messages"][id] = {
        "message": message,
        "time": time,
        "user": user
    }

    data = {
        "message": message,
        "room": room,
        "time": time,
        "user": user,
        "type": db["chatData"][room]["type"],
        "id": id
    }

    if "server_" in str(room):
        data["servername"] = db["servers"][room[15:len(room)]]["name"]
    
    #pusher_client.trigger(socket_id,"messages",db["chatData"][room]["messages"])
    pusher_client.trigger(room,"message",data)
    print("dfdsafadsfdsa", data)
    return "d"






@app.route("/writeDB/", methods=["POST", "GET"])
def write():
  writeDB(db)
  print("db updated!")
  return "DB Written"


app.run(host="0.0.0.0", port=8080, debug=True)
