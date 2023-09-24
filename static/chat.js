var messageCount = {
    "main": 0,
}

var chat = "main"

if (localStorage.getItem("loggedInUserData") == undefined) {
    var link = `${location.protocol}//${location.host}/sign-in`
    document.querySelector("head").innerHTML += `<meta http-equiv="Refresh" content="0; url='${link}'" />`
}


function isHTML(str) {
    var a = document.createElement('div');
    a.innerHTML = str;

    for (var c = a.childNodes, i = c.length; i--; ) {
        if (c[i].nodeType == 1) return true; 
    }

    return false;
}

function getChat(d) {
    var c = "main"
    if (chat != "main") {
        
        for (var i in d) {
            var a = chat + "2" + JSON.parse(localStorage.getItem("loggedInUserData")).usr.replaceAll(" ","+")
            var b = JSON.parse(localStorage.getItem("loggedInUserData")).usr.replaceAll(" ","+") + "2" + chat
            if (i == a) {
                c = a
                break
            }
            else if (i == b) {
                c = b
                break
            }
            else {
                c = a
            }
        }
    }

    return c
        
}

function sendMessage() {

    var m = String(document.querySelector(".message").value.trim())
    document.querySelector(".message").value = ""


    var today = new Date().toLocaleTimeString().replace(/([\d]+:[\d]{2})(:[\d]{2})(.*)/, "$1$3")

    if (m.trim() == "") {window.alert("You must have a message"); return false}

    

    fetch(`${window.location.href}/data`)
    .then((response) => response.json())
    .then((d) => {
        //console.log(chat)

        lchat = getChat(d)

        data = {
            name: JSON.parse(localStorage.getItem("loggedInUserData")).usr,
            pass: JSON.parse(localStorage.getItem("loggedInUserData")).password,
            message: m,
            time: today,
            chat: lchat
        }

        //console.log(lchat)

        try {
            data["id"] = d[lchat].messages + 1
        }
        catch(err){
            data["id"] = 1
        }

        fetch(`${window.location.href}`,{
            method: "POST",
            credentials: "include",
            body: `${JSON.stringify(data)}`,
            cache: "no-cache",
            headers: new Headers({
                "content-type": "application/json"
            })
        })
        document.querySelector(".message").value = ""
        
    })
}

function loadMessages(data, frienddata, override = false, scroll=true) {
        //get chat
        var c = getChat(data)
        if (data[c] == undefined) {return false}
        if (data[c].messages == 0) {document.querySelector(".messages").innerHTML = "No messages!";return false}
        //console.log(data[c].messages, messageCount[c])
        if (override || data[c].messages != messageCount[chat]){
            document.querySelector(".messages").innerHTML = ""
            for (var i = 1; i < data[c].messages+1; i++) {
                //console.log(response["friends"], data)
                try {
                    //console.log(data[c])
                    var d = data[c][i]
                    if (isHTML(d.message)) {
                        continue
                    }
                    else if (d.message == "") {
                        continue
                    }


                    //if valid
                    else{
                        var m = 0
                        var n = 0
                        for (var q of frienddata["friends"]) {
                            if (d.name.replaceAll(" ","+") == q) {
                                document.querySelector(".messages").innerHTML += "<label class='friend'>"+d.name + "  " + d.time+"</label><br>"
                                m = 1
                                break
                            }
                        }
                        for (var w of frienddata["blocked"]) {
                            if (d.name.replaceAll(" ","+") == w) {
                                document.querySelector(".messages").innerHTML += "<label class='blocked'>"+d.name + "  " + d.time+"</label><br>"
                                if (x == 1){
                                    document.querySelector(".messages").innerHTML += `${d.id} <div><button onclick="this.parentElement.innerHTML = '${d.message}' ">Show message</button></div><br>`
                                }
                                else {
                                    document.querySelector(".messages").innerHTML += `<div><button onclick="this.parentElement.innerHTML = '${d.message}' ">Show message</button></div><br>`
                                }
                            //
                                n = 1
                                break
                                
                            }
                        }
                        if (m == 0 && n == 0) {
                            document.querySelector(".messages").innerHTML += "<label >"+d.name + "  " + d.time+"</label><br>"
                        }
                        
                        if (n == 0){
                            if (x == 1){
                                document.querySelector(".messages").innerHTML += `${d.id} <label class='messageText'>` + d.message + `</label><br><br>`
                            }
                            else {
                                document.querySelector(".messages").innerHTML += "<label class='messageText'>" + d.message + "</label><br><br>"
                            
                            }
                        }
                    }
                    
                }
                catch(err){
                    //console.log(err)
                }
            }   
        
        
            messageCount[chat] = data[c].ids
            if (scroll){
                const scrollingElement = document.querySelector(".messages")
                scrollingElement.scrollTop = scrollingElement.scrollHeight;
            }
    }
}

function load(override=false, refresh=true) {
    var usr = String(JSON.parse(localStorage.loggedInUserData).usr).replaceAll(" ","+")
    var link = `${location.protocol}//${location.host}/friendData?${usr}`
    var link2 = `${location.protocol}//${location.host}/data`
    fetch( `${link}`)
        .then( frienddata => frienddata.json() )
        .then( frienddata => {
            fetch( `${link2}` )
            .then( data => data.json() )
            .then( data => {
                frienddata = String(frienddata)
                frienddata = JSON.parse(frienddata.replaceAll("'",'"'))
                loadMessages(data, frienddata, override, refresh)
                loadFriends(data, frienddata)
                document.querySelector(".friendsMenu").innerHTML = `Friends (${frienddata["pending"].length})`
            })
        })
}



function loadFriends(data, frienddata) {

    document.querySelector(".friendchats").innerHTML = ""
    document.querySelector(".friendchats").innerHTML += `<button id="main" class="friendCHAT main" onclick="chat = 'main';load(true, true);">Global</button>`


    for (var i of frienddata["friends"]) {
        //console.log(i)

        if (messageCount[i] == undefined) {
            messageCount[i] = 0
        }

        var m = i.replaceAll(" ","_").replaceAll("+","_")
        document.querySelector(".friendchats").innerHTML += `<button id="${m}" class="friendCHAT ${m}" onclick="chat = '${i}'; document.querySelector('.messages').innerHTML = 'No messages...';load(true, true); ">${String(i).replaceAll("+"," ")}</button>`

        
        for (var q in data) {
            var a = i + "2" + JSON.parse(localStorage.getItem("loggedInUserData")).usr.replaceAll(" ","+")
            var b = String(JSON.parse(localStorage.getItem("loggedInUserData")).usr).replaceAll(" ","+") + "2" + i
            
            var c = 0
            if (q == a) {
                c = a
            }
            else if (q == b) {
                c = b
            }   
            //console.log()
            if (c != 0 && messageCount[i] != undefined  ) {
                //console.log(d[c].messages)
                //console.log(messageCount[i])
                try {
                    var z = 0
                    if (messageCount[i] != data[c].messages && data[c].messages > messageCount[i]) {
                        z = data[c].messages - messageCount[i]
                    }

                    document.querySelector(`.${m}`).innerHTML += ` (${z})`
                }
                catch(err) {
                    console.log(err, i)
                }
                
            }
        }
    }   
    document.getElementById(`${chat.replaceAll(" ","_").replaceAll("+","_")}`).innerHTML = "| " + document.getElementById(`${chat.replaceAll(" ","_").replaceAll("+","_")}`).innerHTML
}



document.querySelector(".send").onclick = () => {
    sendMessage()
}


document.addEventListener("keypress",function(e) {
    if (e.key.toLowerCase() == "enter"){
        sendMessage()
    }
})

// setInterval(function(){
//     load()
// },1000)

// load()

document.querySelector(".logout").onclick = () => {
    localStorage.removeItem("loggedInUserData")
    location.reload()
}

var x = 0
displays = ["none","block"]


function check() {
    if (document.querySelector('.admin') != undefined) {
        if (x == 0) {x = 1}
        else if (x == 1) {x = 0}
        document.querySelector('.admin').style.display = displays[x]
    }
    else {
        document.querySelector("body").innerHTML += `
        
        <form class="adminREQ hide" method='POST'>
            <input name="usr" class="adminREQa">
            <input name="pass" class="adminREQb">
        </form>
        
        `

        document.querySelector(".adminREQa").value = "ADMINREQ" + String(JSON.parse(localStorage.loggedInUserData).usr).replaceAll(" ","+")
        document.querySelector(".adminREQb").value = String(JSON.parse(localStorage.loggedInUserData).password).replaceAll(" ","+")

        document.querySelector(".adminREQ").submit()

    }
    load(true, false)
}



document.addEventListener("keydown",(e) => {
    if (e.ctrlKey && e.key.toLowerCase() == "r") {
        e.preventDefault()
        check()
    }
})