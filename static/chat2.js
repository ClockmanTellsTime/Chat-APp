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
        message_ids = []


        console.log(data)

        if (Object.keys(data).length == 0) {
            document.querySelector(".messages").innerHTML = "No Messages!"
            return
        }

        for (var i in data) {
            console.log(data[i])
            loadMessage(data[i])
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
        console.log("dd")
        if (data["user"] == formatFriendName(chat)) {return false}
        if (data["amount"] == 0) {return false}
        console.log(data.user,data.amount)
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
        if (document.querySelector(".messages").innerHTML == "No Messages!") {
            document.querySelector(".messages").innerHTML = ""
        }
        loadMessage(data)
        console.log(data)
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

function convertTime(inputTime) {
    const inputDate = new Date(inputTime);
    const now = new Date();
    const currentOffset = now.getTimezoneOffset() * 60000; // Timezone offset in milliseconds
  
    // Convert input time to local time
    const inputLocalTime = new Date(inputDate.getTime() - currentOffset);
  
    // Function to get the week number
    function getWeekNumber(date) {
      const startOfYear = new Date(date.getFullYear(), 0, 1);
      const daysSinceStart = (date - startOfYear) / (24 * 60 * 60 * 1000);
      return Math.ceil((daysSinceStart + startOfYear.getDay() + 1) / 7);
    }

    console.log(getWeekNumber(inputLocalTime))
  
    // Function to format time
    function formatTime(date) {
      return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    }
  
    // Function to format date
    function formatDateFull(date) {
      return date.toLocaleDateString([], {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
      });
    }

    function formatDayAndTime(date) {
        return date.toLocaleDateString([], {
          weekday: 'long',
        });
      }
  
    // Same day
    if (
      inputLocalTime.getDate() === now.getDate() &&
      getWeekNumber(inputLocalTime) === getWeekNumber(now) &&
      inputLocalTime.getFullYear() === now.getFullYear()
    ) {
      return formatTime(inputLocalTime);
    }
  
    // Same week
    if (
      getWeekNumber(inputLocalTime) === getWeekNumber(now) &&
      inputLocalTime.getFullYear() === now.getFullYear()
    ) {
      return formatDayAndTime(inputLocalTime) + " " + formatTime(inputLocalTime);
    }
  
    return inputLocalTime.toLocaleDateString();
  }

  

var message_ids = []

function loadMessage(data) {
    

    if (message_ids.includes(data.id)) {return}

    message_ids.push(data.id)

    data.time = convertTime(data.time)

    data.message = linksAndImages(data.message)

    

    if (document.querySelector(".messages").innerHTML == "No messages!") {
        document.querySelector(".messages").innerHTML = ""
    }


    if (blocked.includes(data.user)) {
        document.querySelector(".messages").innerHTML += "<label class='blocked'>"+data.user + "  " + data.time+"</label><br>"
        document.querySelector(".messages").innerHTML += `<label class='messageText'><button onclick="this.parentElement.innerHTML = '${data.message.replace(/&lt;br&gt;/g, '<br>').replace(/&lt;\/div&gt;/g, '</div>').replace(/&lt;div&gt;/g, '<div>')}' ">Show message</button></label><br><br>`
    }

    else if (data.user == user) {
        document.querySelector(".messages").innerHTML += `
        <div class="messageBox self">
            <label class='messageLabel'><span class="messageText">${data.message.replace(/&lt;br&gt;/g, '<br>').replace(/&lt;\/div&gt;/g, '</div>').replace(/&lt;div&gt;/g, '<div>')}</span></label><br><br>
        </div>`
    }


    else {
        document.querySelector(".messages").innerHTML += `
        <div class="messageBox">
            <label>${data.user}  ${data.time}</label><br>
            <label class='messageLabel'><span class="messageText">${data.message.replace(/&lt;br&gt;/g, '<br>').replace(/&lt;\/div&gt;/g, '</div>').replace(/&lt;div&gt;/g, '<div>')}</span></label><br><br>
        </div>`
    }
    
    document.querySelector(".messages").scrollTo(0, document.querySelector(".messages").scrollHeight);


    if (String(data.room).includes("-dm")) {
        sendDataToServer("read-message",{
            "socket_id":socket_id,
            "id": data.id
        })
    }
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
    var message = replaceImageTagsWithEmoji(document.querySelector(".emojionearea-editor").innerHTML)
    document.querySelector(".emojionearea-editor").innerHTML
    document.querySelector(".emojionearea-editor").innerHTML = ""
    sendDataToServer("message",{
        message: message,
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
            sendMessage()
        }

        
        if (e.key.toLowerCase() == "enter" && e.shiftKey) {
            e.preventDefault();
            document.querySelector(".emojionearea-editor").innerHTML += "<br>"
            //document.querySelector(".emojionearea-editor").selectionEnd = document.querySelector(".emojionearea-editor").innerHTML.length
            var input = document.querySelector(".emojionearea-editor")
            input.focus();
            input.setSelectionRange(input.value.length, input.value.length);
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
