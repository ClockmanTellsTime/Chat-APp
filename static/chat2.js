var socketio = io();
socketio.emit("joinroom","global")
socketio.emit("getfrienddata")
socketio.emit("getservers")


var chat = "main"
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


socketio.on("message", function(data) {
    console.log(data)

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
})


socketio.on("frienddata", function(data) {
    console.log(data)

    document.querySelector(".friendchats").innerHTML = ""


    for (var friend of data["friends"]) {
        //console.log(i)
        var friendFormatted = formatFriendName(friend)
        document.querySelector(".friendchats").innerHTML += `<button id="${friendFormatted}" class="friendCHAT ${friendFormatted}" onclick="selectChat('${friend}','${friendFormatted}')">   <div class='nameDisplay ${friendFormatted}ChatButton'>${String(friend).replaceAll("+"," ")}</div></button>`
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
})


socketio.on("serverData",function(data) {
    console.log(data)


    document.querySelector(".serverMenu").innerHTML = `
    <br><button id="main" class="serverChat main" onclick="selectChat('main','main');socketio.emit('getfrienddata')">Global</button><br><br>
    `

    for (var i in data) {
        console.log(data[i].name)

        var name = "server_"+data[i].id

        document.querySelector(".serverMenu").innerHTML += `<button class="serverChat" id="${name}" onclick="selectChat('${name}'); socketio.emit('getservermembers','${data[i].id}') ">${data[i].name}</button><br><br>`
    
        if (chat == name){
            socketio.emit('getservermembers',`${data[i].id}`) 
        }
    }

    selectChat(chat, formatFriendName(chat))



    document.querySelector(".serverMenu").innerHTML += `
    <a href="/createserver"><button class="serverChat createGroupChat">+ Create Group Chat</button></a><br></br>
    `

    
})

socketio.on("servermembers",function(data) {
    console.log(data)
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
})


socketio.on("allmessages",function(data){
    console.log(data)
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


socketio.on("reload", function() {
    location.reload()
})

socketio.on("dm", function(data) {
    console.log(data)

    if (data["user"] == formatFriendName(chat)) {return false}
    if (data["amount"] == 0) {return false}

    addNotification(data["user"], data["amount"])
})

socketio.on("logout", function() {
    document.querySelector(".logout").click()
})



function sendMessage() {
    var message = String(document.querySelector(".message").value.trim())
    var time = new Date().toLocaleTimeString().replace(/([\d]+:[\d]{2})(:[\d]{2})(.*)/, "$1$3")

    document.querySelector(".emojionearea-editor").innerHTML

    document.querySelector(".emojionearea-editor").innerHTML = ""
    document.querySelector(".message").value = ""

    socketio.emit("message", message, time)

}



function selectChat(friend) {
    document.querySelector(".messages").innerHTML = "Loading..."
    console.log(friend)

    if (friend=="main"){
        socketio.emit('joinroom','global')
        chat = 'main'
    }

    if (String(friend).startsWith("server_")) {
        socketio.emit('joinroom',friend)
        chat = friend
    }

    else {
        socketio.emit('joindm',friend)
        chat = friend
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

document.querySelector(".logout").onclick = () => {
    socketio.emit("logout")
}








setTimeout(function() {
    document.addEventListener("keyup",function(e) {

        console.log(e.which);

        if (e.key.toLowerCase() == "enter" && e.ctrlKey) {
            e.preventDefault();
            var message = replaceImageTagsWithEmoji(document.querySelector(".emojionearea-editor").innerHTML)
            var time = new Date().toLocaleTimeString().replace(/([\d]+:[\d]{2})(:[\d]{2})(.*)/, "$1$3")
        
            document.querySelector(".emojionearea-editor").innerHTML = ""
        
            socketio.emit("message", message, time)
            console.log("e")
        }
    })
},100)

