from flask import Flask, request, render_template, redirect, url_for, session, jsonify, Response
import json
import random
from bs4 import BeautifulSoup
import pusher
from datetime import datetime
import hashlib
import hmac
import string
import os
import re
import time

folder_path = "static"

a = str(time.time())

css_number = a
js_number = a



# Rename the files now
for filename in os.listdir(folder_path):
    if  str(filename).startswith("chat"):
          extension = filename.split(".")[2]
          
          if extension == 'css':
              new_filename = f"chat{css_number}.{extension}"
          elif extension == 'js':
              new_filename = f"chat{js_number}.{extension}"
          
          old_path = os.path.join(folder_path, filename)
          new_path = os.path.join(folder_path, new_filename)
          
          os.rename(old_path, new_path)
          print(f"Renamed {filename} to {new_filename}")


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



db = openDB()
db["chatData"]["global"]["messages"] = {}
writeDB(db)

#Clear rooms in the thing
for user in db["userdata"]:
  db["userdata"][user]["online"] = False



def is_html(input_str):
    input_str = str(input_str).replace("&lt;","<").replace("&gt;",">")
    try:
        soup = BeautifulSoup(input_str, "html.parser")
        return any(tag.name != 'br' and tag.name != 'div' for tag in soup.find_all(True))
    except:
        return False

def hash_string(string_to_hash):
    # Encode the string to bytes before hashing
    encoded_string = string_to_hash.encode('utf-8')
    
    # Create a hash object using SHA-256 algorithm
    hasher = hashlib.sha256()
    
    # Update the hash object with the encoded string
    hasher.update(encoded_string)
    
    # Get the hexadecimal representation of the hash
    hashed_string = hasher.hexdigest()
    
    return hashed_string

def generate_random_string(n=10):
    # Define the characters to choose from for the random string
    characters = string.digits  # Use digits for a 10-digit string
    
    # Generate a random 10-character string
    random_string = ''.join(random.choice(characters) for _ in range(n))
    
    return random_string

def most_alphabetical_order(word1, word2):
    sorted_words = sorted([word1, word2])
    return sorted_words[0]  # Returns the word that comes last alphabetically

def least_alphabetical_order(word1, word2):
    sorted_words = sorted([word1, word2])
    return sorted_words[1]  


def generate_hmac_sha256(message):
    # Convert the key and message to bytes if they're not already in bytes
    key_bytes = bytes("b4805fbd535ae0d56573", 'utf-8') if isinstance("b4805fbd535ae0d56573", str) else "b4805fbd535ae0d56573"
    message_bytes = bytes(message, 'utf-8') if isinstance(message, str) else message

    # Generate the HMAC using SHA256
    hmac_sha256 = hmac.new(key_bytes, message_bytes, hashlib.sha256)

    # Get the hexadecimal representation of the digest
    hmac_hexdigest = hmac_sha256.hexdigest()
    
    return hmac_hexdigest

app = Flask(__name__)
app.config["SECRET_KEY"] = generate_random_string(20)




@app.route("/webhook", methods=['POST'])
def pusher_webhook():
  # pusher_client is obtained through pusher_client = pusher.Pusher( ... )
  webhook = pusher_client.validate_webhook(
    key=request.headers.get('X-Pusher-Key'),
    signature=request.headers.get('X-Pusher-Signature'),
    body=request.data
  )

  for event in webhook['events']:
    if event['name'] == "channel_occupied":
      if "user-" in event["channel"]:
          user = str(event["channel"]).split("user-")[1].split("-")[0]
          print(str(user) + " has become online!")


          if not user in db["userdata"]:
              db["userdata"][user] = {}

          db["userdata"][user]["online"] = True

          if not user in db["users"]:
              return "ok"

          for friend in db["users"][user]['friendData']["friends"]:       
            data = {
                "user": user,
                "online": db["userdata"][user]["online"]
            }

            pusher_client.trigger("private-user-"+friend,"whosonline",data)

    elif event['name'] == "channel_vacated":
        if "user-" in event["channel"]:
          user = str(event["channel"]).split("user-")[1].split("-")[0]
          print(str(user) + " has gone offline!")


          if not user in db["userdata"]:
              db["userdata"][user] = {}

          db["userdata"][user]["online"] = False

          if not user in db["users"]:
              return "ok"

          for friend in db["users"][user]['friendData']["friends"]:     
              data = {
                  "user": user,
                  "online": db["userdata"][user]["online"]
              }

              pusher_client.trigger("private-user-"+friend,"whosonline",data)

  return "ok"



@app.route("/", methods=["POST", "GET"])
def join():

  user = session.get("user")

  if not user or user == "":
    return redirect(url_for("signin"))

  return render_template("chat.html",css=css_number,js=js_number)


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
    writeDB(db)
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
    salt = generate_random_string()
    password = hash_string(request.form.get("pass") + salt)

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
          "salt": salt,
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

      session["id"] = usr +"-"+str(random.randint(1, 1000000000000000))
      writeDB(db)
      return redirect(url_for("join"))

  return render_template("signup.html", r="")


@app.route("/sign-in", methods=["POST", "GET"])
def signin():
  user = session.get("user")

  if user and user != "":
    return redirect(url_for("join"))

  if request.method == "POST":
    usr = request.form.get("usr")
    password = hash_string(request.form.get("pass"))
    

    if usr == "":
      return render_template("signin.html", r="You must have a username...")

    if password == "":
      return render_template("signin.html", r="You must have a password...")

    if usr in db["users"].keys():
      
      salt = db["users"][usr]["salt"]
      password = hash_string(request.form.get("pass") + salt)

      if db["users"][usr]["banned"]:
        return render_template("banned.html", usr=usr)

      if db["users"][usr]["password"] == password:
        session["user"] = usr
        session["id"] = usr + "-" +str(random.randint(1, 1000000000000000))
        return redirect(url_for("join"))

      else:
        return render_template("signin.html",r="Password and/or Username is incorrect!",usr=usr)
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

          if not "server_" + str(id) in db["chatData"]:
            db["chatData"]["server_" + str(id)] = {"messages": {}, "ids": 0}

          db["chatData"]["server_" + str(id)]["members"] = db["servers"][id]["members"]


      if action == "add":
        name = request.form.get("name")

        if (not name in db["servers"][id]["members"]
            and not id in db["users"][name]["servers"]
            and name in db["users"][user]["friendData"]["friends"]):
          db["servers"][id]["members"].append(name)
          db["users"][name]["servers"].append(id)

          if not "server_" + str(id) in db["chatData"]:
            db["chatData"]["server_" + str(id)] = {"messages": {}, "ids": 0}


          db["chatData"]["server_" + str(id)]["members"] = db["servers"][id]["members"]

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
          
          try:
            del db["chatData"]["server_" + str(id)]
          except:
              pass
          
          try:
            del db["servers"][id]
          except:
              pass

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


        servers = db["users"][member]["servers"]

        serverData = {}

        for server in servers:
            serverData[server] = {
                "owner": db["servers"][str(server)]["owner"],
                "name": db["servers"][str(server)]["name"],
                "members": db["servers"][str(server)]["members"],
                "id": server,
            }


        pusher_client.trigger("private-user-"+member,"servers",serverData)

        pusher_client.trigger("private-user-"+member,"servermembers",serverData)


  writeDB(db)
  if str(id) in db["servers"].keys():
    if user == db["servers"][str(id)]["owner"]:
      return render_template("configure.html",server=db["servers"][str(id)]["name"],id=id)

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

    pusher_client.trigger("private-user-"+member,"servermembers",data)

  writeDB(db)
  return redirect(url_for("join"))








@app.route("/friendrequest", methods=["POST", "GET"])
def friendrequest():
  user = session.get("user")
  data = request.json
  socket_id = data.get("socket_id","")
  friend = data.get("friendUSR","")


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

  pusher_client.trigger("private-user-"+friend,"friends",db["users"][friend]["friendData"])
  pusher_client.trigger("private-user-"+user,"friends",db["users"][user]["friendData"])
  writeDB(db)
  return "ok"


@app.route("/blockuser", methods=["POST", "GET"])
def blockuser():
  user = session.get("user")
  data = request.json
  socket_id = data.get("socket_id","")
  friend = data.get("friendUSR","")


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

  pusher_client.trigger("private-user-"+friend,"friends",db["users"][friend]["friendData"])
  pusher_client.trigger("private-user-"+user,"friends",db["users"][user]["friendData"])
  writeDB(db)
  return "ok"


@app.route("/removefriend", methods=["POST", "GET"])
def removefriend():
  data = request.json
  user = session.get("user")
  friend = data.get("friendUSR","")
  socket_id = data.get("socket_id","")

  if not user or user == "":
    return redirect(url_for("signin"))

  if user != friend and user in db["users"] and friend in db["users"]:
    db["users"][user]["friendData"]["friends"].remove(friend)
    db["users"][friend]["friendData"]["friends"].remove(user)


  pusher_client.trigger("private-user-"+friend,"friends",db["users"][friend]["friendData"])
  pusher_client.trigger("private-user-"+user,"friends",db["users"][user]["friendData"])
  writeDB(db)
  return "ok"


@app.route("/unblockuser", methods=["POST", "GET"])
def unblockuser():
  user = session.get("user")
  data = request.json
  socket_id = data.get("socket_id","")
  friend = data.get("friendUSR","")


  if not user or user == "":
    return redirect(url_for("signin"))
  
  if (user != friend and friend in db["users"] and user in db["users"] and friend in db["users"][user]["friendData"]["blocked"] and user in db["users"][friend]["friendData"]["blockedby"]):
    db["users"][user]["friendData"]["blocked"].remove(friend)
    db["users"][friend]["friendData"]["blockedby"].remove(user)

  
  pusher_client.trigger("private-user-"+friend,"friends",db["users"][friend]["friendData"])
  pusher_client.trigger("private-user-"+user,"friends",db["users"][user]["friendData"])
  writeDB(db)
  return "ok"


@app.route("/cancelfriendrequest", methods=["POST", "GET"])
def cancelfriendrequest():
  data = request.json
  user = session.get("user")
  friend = data.get("friendUSR","")

  if not user or user == "":
    return redirect(url_for("signin"))

  if (friend in db["users"][user]["friendData"]["outgoing"]
      and user in db["users"][friend]["friendData"]["pending"]):
    db["users"][user]["friendData"]["outgoing"].remove(friend)
    db["users"][friend]["friendData"]["pending"].remove(user)

  pusher_client.trigger("private-user-"+friend,"friends",db["users"][friend]["friendData"])
  pusher_client.trigger("private-user-"+user,"friends",db["users"][user]["friendData"])
  writeDB(db)
  return "ok"


@app.route("/acceptfriendrequest", methods=["POST", "GET"])
def acceptfriendrequest():
  user = session.get("user")
  data = request.json
  socket_id = data.get("socket_id","")
  friend = data.get("friendUSR","")


  if not user or user == "":
    return redirect(url_for("signin"))

  if (friend in db["users"][user]["friendData"]["pending"] and user in db["users"][friend]["friendData"]["outgoing"]):
    db["users"][user]["friendData"]["friends"].append(friend)
    db["users"][friend]["friendData"]["friends"].append(user)

    db["users"][user]["friendData"]["pending"].remove(friend)
    db["users"][friend]["friendData"]["outgoing"].remove(user)

  pusher_client.trigger("private-user-"+friend,"friends",db["users"][friend]["friendData"])
  pusher_client.trigger("private-user-"+user,"friends",db["users"][user]["friendData"])
  writeDB(db)
  return "ok"


@app.route("/declinefriendrequest", methods=["POST", "GET"])
def declinefriendrequest():
  user = session.get("user")
  data = request.json
  socket_id = data.get("socket_id","")
  friend = data.get("friendUSR","")


  if not user or user == "":
    return redirect(url_for("signin"))

  if (friend in db["users"][user]["friendData"]["pending"]
      and user in db["users"][friend]["friendData"]["outgoing"]):
    db["users"][user]["friendData"]["pending"].remove(friend)
    db["users"][friend]["friendData"]["outgoing"].remove(user)

  pusher_client.trigger("private-user-"+friend,"friends",db["users"][friend]["friendData"])
  pusher_client.trigger("private-user-"+user,"friends",db["users"][user]["friendData"])
  writeDB(db)
  return "ok"



@app.route("/connect",methods=["POST","GET"])
def connect():
    data = request.json
    socketid = data.get('socketId', '')
    url = data.get("url","")

    session["url"] = url
    session["socketid"] = socketid

    print(session.get("user") + " has connected at " + url)

    return "ok"


def authenticate_channel(user,name,id):
    if "dm-" in name or "server-" in name:
        if user in db["chatData"][name]["members"]:
            return True
        else:
            return False
        
    return True


@app.route('/pusher/user-auth', methods=['POST'])
def pusher_auth_user():
    socket_id = request.form['socket_id']

    user_data = '{"id": "'+session.get("id")+'","user_info": {"name":"'+ session.get("user")+'"}}'

    mmm = str(socket_id) + "::user::"+str(user_data)

    response = {
        'auth': "3ee636d6edcdecffe90e:"+generate_hmac_sha256(mmm),
        "user_data": user_data,
        "user_info": {
            "name": str(session.get("user"))
        }
    }

    return jsonify(response)

@app.route('/pusher/auth', methods=['POST'])
def pusher_auth():
    channel_name = request.form['channel_name']
    socket_id = request.form['socket_id']
    user = session.get("user")
    
    if authenticate_channel(user,channel_name, socket_id):
        response = pusher_client.authenticate(
            channel=channel_name,
            socket_id=socket_id
        )
        return jsonify(response)
    else:
        response = "not allowed!"
        return response, 403  # Access forbidden


def get_usernames(string):
    # Split the string by '2'
    parts = string.split('2')
    
    # Check if there are at least two parts separated by '2'
    if len(parts) >= 2:
        username1 = parts[0][len('presence-dm-'):]  # Extract the first username
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

    if not room in db["chatData"]:
        if "server" in str(room):
            id = str(room).split("server-")[1]

            if str(id) in db["servers"]:
                db["chatData"][room] = {
                    "messages": {},
                    "ids": 0,
                    "type": "groupchat",
                    "members": db["servers"][str(id)]["members"],
                }
        else:
            db["chatData"][room] = {
                "messages": {},
                "ids": 0,
                "type": "dm",
                "members": get_usernames(room),
            }



    if "dm-" in room or "server-" in room:
        if not user in db["chatData"][room]["members"]:
            return True

    if "-dm" in str(room):
      #update messages read in that thing
      if not user in db["userdata"]:
        db["userdata"][user] = {}

      if not room in db["userdata"][user]:
        db["userdata"][user][room] = {}

      db["userdata"][user][room] = {
          "read": db["chatData"][room]["ids"]
      }


    try:
      pusher_client.trigger("private-socket_id-"+socket_id,"messages",db["chatData"][room]["messages"])
    except:
        for message in db["chatData"][room]["messages"]:
          data = db["chatData"][room]["messages"][message]
          pusher_client.trigger("private-socket_id-"+socket_id,"message",data)

    writeDB(db)
    return "ok"

@app.route('/get-friends', methods=['POST'])
def get_friends():
    data = request.json
    socket_id = data.get("socket_id","")
    user = session.get("user")
    
    pusher_client.trigger("private-socket_id-"+socket_id,"friends",db["users"][user]["friendData"])

    #show all dms!
    for friend in db["users"][user]["friendData"]["friends"]:
        room = "presence-dm-" + most_alphabetical_order(user,friend) + "2"+least_alphabetical_order(user,friend)
        
        if room in db["chatData"]:
            if not user in db["userdata"]:
                db["userdata"][user] = {}

            if not room in db["userdata"][user]:
                db["userdata"][user][room] = {"read":0}

            data = {
                "user": room,
                "amount": db["chatData"][room]["ids"] - db["userdata"][user][room]["read"]
            }

            pusher_client.trigger("private-socket_id-"+socket_id,"dm",data)


    #show all online people
    for friend in db["users"][user]["friendData"]["friends"]:
        if friend in db["userdata"]:
            data = {
                "user": friend,
                "online": db["userdata"][friend]["online"]
            }

            pusher_client.trigger("private-socket_id-"+socket_id,"whosonline",data)

        else:
            data = {
                "user": friend,
                "online": False
            }
            pusher_client.trigger("private-socket_id-"+socket_id,"whosonline",data)

    writeDB(db)
    return "ok"

@app.route('/servermembers', methods=['POST'])
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

        pusher_client.trigger("private-socket_id-"+socket_id,"servermembers",data)
    writeDB(db)
    return "ok"



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


    pusher_client.trigger("private-socket_id-"+socket_id,"servers",serverData)
    writeDB(db)
    return "ok"



@app.route('/message', methods=['POST'])
def message():
    data = request.json
    socket_id = data.get("socket_id","")
    user = session.get("user")
    room = session.get("room")
    message = data.get("message","")
    
    time = str(datetime.utcnow())

    if not user or user == "":
        return False

    if not room:
        return False

    if message == "":
        return 'ok'

    if is_html(message):
        
        return 'ok'

    if len(message) > 2500:
        return 'ok'

    if not room in db["chatData"]:
        db["chatData"][room] = {"messages": {}, "ids": 0,"members":[]}
        if "dm" in room:
          db["chatData"][room]["type"] = "dm"
        if "server" in room:
          db["chatData"][room]["type"] = "server"


    db["chatData"][room]["ids"] += 1

    id = str(db["chatData"][room]["ids"])

    db["chatData"][room]["messages"][id] = {
        "message": message,
        "room": room,
        "time": time,
        "user": user,
        "type": db["chatData"][room]["type"],
        "id": id
    }


    if "server" in str(room):
        db["chatData"][room]["messages"][id]["servername"] = db["servers"][room[16:len(room)]]["name"]

    if "-dm" in str(room):
        username1, username2 = get_usernames(room)


        db["chatData"][room]["messages"][id][username1+"_read_at"] = ""
        db["chatData"][room]["messages"][id][username2+"_read_at"] = ""

        db["chatData"][room]["messages"][id][user+"_read_at"] = str(datetime.utcnow())

        other_user = ""
        if user == username1:
            other_user = username2
        else:
            other_user = username1

        

        if not user in db["userdata"]:
            db["userdata"][user] = {}

        db["userdata"][user][room] = {
            "read": db["chatData"][room]["ids"]
        }

        if not other_user in db["userdata"]:
            db["userdata"][other_user] = {}

        if not room in db["userdata"][other_user]:
            db["userdata"][other_user][room] = {
                "read": 0
            }

        data = {
            "user": room,
            "amount": db["chatData"][room]["ids"] - db["userdata"][other_user][room]["read"]
        }

        pusher_client.trigger("private-user-"+other_user,"dm",data)


    data = db["chatData"][room]["messages"][id]
    pusher_client.trigger(room,"message",data)
    writeDB(db)
    return "ok"


@app.route('/read-message', methods=['POST'])
def read_message():
    data = request.json
    user = session.get("user")
    room = session.get("room")
    id = str(data.get("id",""))
    socket_id = data.get("socket_id","")

    #make sure room is a dm
    if not "dm" in str(room):
        return "ok"

    #update time read and amount of messages read!
    if db["chatData"][room]["messages"][id][user+"_read_at"] == "":
      db["chatData"][room]["messages"][id][user+"_read_at"] = str(datetime.utcnow())
      db["userdata"][user][room]["read"] = db["chatData"][room]["ids"]


      username1, username2 = get_usernames(room)

      other_user = ""
      if user == username1:
          other_user = username2
      else:
          other_user = username1
      
      data = {
          "time":db["chatData"][room]["messages"][id][user+"_read_at"],
          "room": room,
          "id": id,
      }
      pusher_client.trigger("private-user-"+other_user,"messageread",data)
    writeDB(db)
    return "ok"



@app.route("/writeDB/", methods=["POST", "GET"])
def write():
  writeDB(db)
  return "DB Written"



if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080, debug=True)
