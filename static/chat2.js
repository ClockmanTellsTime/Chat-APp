var pusher = new Pusher('3ee636d6edcdecffe90e', {
    cluster: 'us3',
    encrypted: true,
});
var socket_id = ""

pusher.connection.bind('connected', function() {
    socket_id = pusher.connection.socket_id;
    console.log('Socket ID:', socket_id);
    sendDataToServer("connect",{
        event_type: "connect",
        url: new URL(location.href).pathname,
        socketId: socket_id
    })

    var only_you_channel = pusher.subscribe(socket_id)
    var all_your_accounts = pusher.subscribe(user)

    only_you_channel.bind("messages",function(data) {
        document.querySelector(".messages").innerHTML = ""
        

        for (var i in data) {


            data[i].message = linksAndImages(data[i].message)
            

            if (blocked.includes(data[i].user)) {
                document.querySelector(".messages").innerHTML += "<label class='blocked'>"+data[i].user + "  " + data[i].time+"</label><br>"
                document.querySelector(".messages").innerHTML += `<label class='messageText'><button onclick="this.parentElement.innerHTML = '${data[i].message}' ">Show message</button></label><br><br>`
            }
        
            else if (data[i].user == user) {
                document.querySelector(".messages").innerHTML += `
                <div class="messageBox self">
                    <label class='messageLabel'><span class="messageText">${data[i].message}</span></label><br><br>
                </div>`
            }
        
            else {
                document.querySelector(".messages").innerHTML += `
                <div class="messageBox">
                    <label class='userLabel'><span class="messageText">${data[i].user}  ${data[i].time}</span></label>

                    <label class='messageLabel'><span class="messageText">${data[i].message}</span></label>
                </div>`
            }
        }

        if (document.querySelector(".messages").innerHTML == "") {
            document.querySelector(".messages").innerHTML = "No messages!"
        }

        document.querySelector(".messages").scrollTo(0, document.querySelector(".messages").scrollHeight);
    })

    only_you_channel.bind("friends",function(data) {
        loadFriends(data)
    })

    all_your_accounts.bind("friends",function(data) {
        loadFriends(data)
    })

    only_you_channel.bind("servers",function(data) {
        loadServers(data)
    })

    all_your_accounts.bind("servers",function(data) {
        loadServers(data)
    })

    only_you_channel.bind("servermembers",function(data) {
        loadServerMembers(data)
    })

    only_you_channel.bind("dm",function(data) {
        if (data["user"] == formatFriendName(chat)) {return false}
        if (data["amount"] == 0) {return false}
    
        addNotification(data["user"], data["amount"])
    })

    all_your_accounts.bind("dm",function(data) {
        if (data["user"] == formatFriendName(chat)) {return false}
        if (data["amount"] == 0) {return false}
    
        addNotification(data["user"], data["amount"])
    })


    

    joinChat("global")
    sendDataToServer("get-friends",{"socket_id":socket_id})
    sendDataToServer("get-servers",{"socket_id":socket_id})
});


function joinChat(name) {
    pusher.unsubscribe(chat)
    var chat_ = pusher.subscribe(name);
    console.log(name)

    chat_.bind('pusher:subscription_error', function(status) {
        if (status.status === 403) {
            console.error('Subscription failed. Access forbidden.');
        }
        console.log(status.error)
    });

    chat_.bind("message",function(data) {
        loadMessage(data)
    })

    if (name == "global") {
        try {
            document.querySelector("body > div.chatMenu > div.friendchats > div").style.display = "none"
        }
        catch(e){}
    }
    
    sendDataToServer("get-messages",{
        "room":name,
        "socket_id":socket_id
    })
}



//   {
//     event_type: 'my-event',
//     message: "Hi",
// }

function sendDataToServer(endpoint,data) {

    fetch(`/${endpoint}`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
}


function loadFriends(data) {
    

    document.querySelector(".friendchats").innerHTML = ""


    for (var friend of data["friends"]) {
        var friendFormatted = formatFriendName(friend)
        var chatFormatted = "private-dm-"+mostAlphabeticalOrder(friendFormatted,user) + "2" + leastAlphabeticalOrder(friendFormatted,user)
        document.querySelector(".friendchats").innerHTML += `<button id="${chatFormatted}" class="friendCHAT ${chatFormatted}" onclick="selectChat('${chatFormatted}','${chatFormatted}')">   <div class='nameDisplay ${chatFormatted}ChatButton'>${String(friend).replaceAll("+"," ")}</div></button>`
    } 

    for (blockedUser of data["blocked"]) {
        blocked.push(blockedUser)
    }

    for (friend of data["friends"]) {
        friends.push(friend)
    }

    var friendRequests = data["pending"].length

    if (friendRequests > 999) {
        friendRequests = "999+"
    }

    document.querySelector(".friendsMenu").innerHTML = `<div class='nameDisplay'>Friends</div>`

    if (friendRequests > 0) {
        document.querySelector(".friendsMenu").innerHTML += `<div class="notifications">${friendRequests}</div>`
    }
}

function loadServers(data) {
    


    document.querySelector(".serverMenu").innerHTML = `
    <br><button id="global" class="serverChat global" onclick="selectChat('global','global');">Global</button><br><br>
    `

    for (var i in data) {

        var name = "private-server-"+data[i].id

        document.querySelector(".serverMenu").innerHTML += `<button class="serverChat" id="${name}" onclick="selectChat('${name}')">${data[i].name}</button><br><br>`
    
        if (chat == name){
            sendDataToServer("servermembers",{
                "socket_id":socket_id,
                "server_id": data[i].id
            })
        }
    }

    selectChat(chat, formatFriendName(chat))



    document.querySelector(".serverMenu").innerHTML += `
    <a href="/createserver"><button class="serverChat createGroupChat">+ Create Group Chat</button></a><br></br>
    `

}
function loadServerMembers(data) {
    
    document.querySelector(".friendchats").innerHTML = `<div class='bar'>${data["server"]}&nbsp;</div>`

    if (data["owner"] == user) {
        document.querySelector(".bar").innerHTML += `<a class="configure" href="/configure/${data["id"]}">configure server</a>`
    }
    else {
        document.querySelector(".bar").innerHTML += `<a class="configure" href="/leave/${data["id"]}">leave server</a>`
    }

    for (var friend of data["members"]) {
        var friendFormatted = formatFriendName(friend)
        document.querySelector(".friendchats").innerHTML += `<button class="friendCHAT" >   <div class='nameDisplay'>${String(friend).replaceAll("+"," ")}</div></button>`
    } 
}


var message_ids = []

function loadMessage(data) {
    

    if (message_ids.includes(data.id)) {return}

    message_ids.push(data.id)

    data.message = linksAndImages(data.message)

    

    if (document.querySelector(".messages").innerHTML == "No messages!") {
        document.querySelector(".messages").innerHTML = ""
    }


    if (blocked.includes(data.user)) {
        document.querySelector(".messages").innerHTML += "<label class='blocked'>"+data.user + "  " + data.time+"</label><br>"
        document.querySelector(".messages").innerHTML += `<label class='messageText'><button onclick="this.parentElement.innerHTML = '${data.message}' ">Show message</button></label><br><br>`
    }

    else if (data.user == user) {
        document.querySelector(".messages").innerHTML += `
        <div class="messageBox self">
            <label class='messageLabel'><span class="messageText">${data.message}</span></label><br><br>
        </div>`
    }


    else {
        document.querySelector(".messages").innerHTML += `
        <div class="messageBox">
            <label>${data.user}  ${data.time}</label><br>
            <label class='messageLabel'><span class="messageText">${data.message}</span></label><br><br>
        </div>`
    }

    document.querySelector(".messages").scrollTo(0, document.querySelector(".messages").scrollHeight);
}


var chat = "global"
var blocked = []
var friends = []

function replaceLinksWithAnchorTags(inputString) {
  // Define a regular expression pattern to match URLs


  var urlPattern = /https?:\/\/\S+/g;

  // Use the replace() method to replace URLs with anchor tags
  var replacedString = inputString.replace(urlPattern, function (match) {
    return '<a href="' + match + '">' + match + '</a>';
  });

  return replacedString;
}

function replaceUnicodeEscapesWithEmoji(input) {
  return input.replace(/\\u([0-9a-fA-F]{4})/g, (match, capture) => {
    return String.fromCharCode(parseInt(capture, 16));
  });
}


function linksAndImages(inputString) {
  inputString = replaceUnicodeEscapesWithEmoji(inputString)
  
  // Define a regular expression pattern to match image URLs

  var imageUrls = inputString.split(/\s+/);
  var imageUrlPattern = /(https?:\/\/[^\s]+\/\S+\.(jpg|jpeg|png|gif|bmp|svg))|(data:image\/[^\s]+;base64,[^\s]+)/gi;

  // Use the replace() method to replace image URLs with image tags
  var replacedString = inputString.replace(imageUrlPattern, function (match) {
    if (match.startsWith("data:image")) {
      return '<br><img src="' + match + '" width="200" height="200"><br>';
    } else {
      return '<br><img src="' + match + '" width="200" height="200"><br>';
    }
  });

  if (replacedString == inputString) {
    replacedString = replaceLinksWithAnchorTags(inputString)
  }
  return replacedString;
}














function sendMessage() {
    var message = String(document.querySelector(".message").value.trim())
    var time = new Date().toLocaleTimeString().replace(/([\d]+:[\d]{2})(:[\d]{2})(.*)/, "$1$3")

    document.querySelector(".emojionearea-editor").innerHTML

    document.querySelector(".emojionearea-editor").innerHTML = ""
    document.querySelector(".message").value = ""

    sendDataToServer("message",{
        message: message,
        time: time,
        socket_id: socket_id
    })

}



function selectChat(friend) {
    document.querySelector(".messages").innerHTML = "Loading messages..."
    console.log(friend)
    joinChat(friend)
    chat = friend

    if (friend == "global"){
        sendDataToServer("get-friends",{"socket_id":socket_id})
    }
    if (String(friend).includes("server")){
        var id = String(friend).split("server-")[1]
        sendDataToServer("servermembers",{"socket_id":socket_id,"server_id": id})
    }
    

    chooseChat(formatFriendName(friend))
}

function chooseChat(friendFormatted) {
    var ancestor = document.querySelector('.friendchats'),
    descendents = ancestor.getElementsByTagName('*');

    for (var i = 0; i < descendents.length; ++i) {
        var button = descendents[i]

        button.style.backgroundColor = ""
        button.style.color = "black"
    }

    var ancestor = document.querySelector('.serverMenu'),
    descendents = ancestor.getElementsByTagName('*');

    for (var i = 0; i < descendents.length; ++i) {
        var button = descendents[i]

        button.style.backgroundColor = ""
        button.style.color = "black"
    }

    document.querySelector(`#${friendFormatted}`).style.backgroundColor = "rgb(50,50,50)"

    try{
        document.querySelector(`#${friendFormatted}`).style.color = "white"
    }
    catch(e){}



    try{
        document.querySelector(`.${friendFormatted}ChatButton`).style.color = "white"
    }
    catch(e){}


    if (document.querySelector(`#${friendFormatted} > div.notifications`) != null) {

        document.querySelector(`#${friendFormatted}`).removeChild(document.querySelector(`#${friendFormatted} > div.notifications`))
    }
}

function addNotification(dm, amount) {
    if (amount >= 100) {
        amount = "99+"
    }

    if (document.querySelector(`#${dm} > div.notifications`) != null) {
        document.querySelector(`#${dm} > div.notifications`).innerHTML = amount
    }

    else {
        try{
        document.querySelector(`#${dm}`).innerHTML += `<div class="notifications">${amount}</div>`
        }
        catch(err){}
    }
}

function formatFriendName(name) {
    return name.replaceAll(" ","_").replaceAll("+","_")
}


function replaceImageTagsWithEmoji(htmlString) {
    // Use regular expressions to find and replace image tags with emojis
    const replacedHtml = htmlString.replace(/<img.*?alt=["'](.*?)["'].*?>/g, (match, altText) => {
      return altText; // Replace the image tag with the alt text (emoji)
    });

    return replacedHtml;
}   


document.querySelector(".send").onclick = () => {
    sendMessage()
}







setTimeout(function() {
    document.addEventListener("keyup",function(e) {


        if (e.key.toLowerCase() == "enter" && e.ctrlKey) {
            e.preventDefault();
            var message = replaceImageTagsWithEmoji(document.querySelector(".emojionearea-editor").innerHTML)
            var time = new Date().toLocaleTimeString().replace(/([\d]+:[\d]{2})(:[\d]{2})(.*)/, "$1$3")
        
            document.querySelector(".emojionearea-editor").innerHTML = ""
        
            sendDataToServer("message",{
                message: message,
                time: time,
                socket_id: socket_id
            })
        }
    })
},100)

function mostAlphabeticalOrder(word1, word2) {
    const sortedWords = [word1, word2].sort();
    return sortedWords[0]; // Returns the word that comes last alphabetically
}

// Function to return words in least alphabetical order
function leastAlphabeticalOrder(word1, word2) {
    const sortedWords = [word1, word2].sort();
    return sortedWords[1]; // Returns the word that comes first alphabetically
}
