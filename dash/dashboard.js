var api_address, robot_ip, port

function $(elementID) {
    return document.getElementById(elementID)
}

function connect() {
    robot_ip = $("robot_ip").value
    port = 9559
    api_address = $("api_ip").value

    if (robot_ip == "") {
        robot_ip = "192.168.1.3"
    }
    else if (robot_ip.indexOf(":") != -1) {
        port = robot_ip.slice(robot_ip.indexOf(":") + 1, robot_ip.length)
        robot_ip = robot_ip.slice(0, robot_ip.indexOf(":"))
    }

    if (api_address == "") {
        api_address = "http://127.0.0.1:5000/api"
    }


    fetch(api_address+"/connect", {
        method: "POST",
        //mode: "no-cors",
        body: JSON.stringify({
            ip: robot_ip,
            port: port
        }),
        headers: {
            "Content-type": "application/json"
        }
    })

}

function enactCommand(elementID) {
    console.log(elementID)
    let commandName, arguments
    commandName = elementID.slice(0, elementID.indexOf(":"))

    //check if elementID has arguments in it, and if so include them
    if(elementID.indexOf(":") != elementID.length){
        arguments = [elementID.slice(elementID.indexOf(":")+1)]
    }

    if (commandName == "SayText") {
        arguments = [$("say_text_textbox").value]
    }
    else if (commandName == "PointAt") {
        let left = $("left_arm").checked, right = $("right_arm").checked
        if (left && right) {
            arguments.push("both")
        }
        else if (left) {
            arguments.push("left")
        }
        else {
            arguments.push("right")
        }
    }

    fetch(api_address+"/behavior", {
        method: "POST",
        body: JSON.stringify(
            {
                intent: "default intent",
                description: "default description",
                actionList: [
                    {
                        name: commandName,
                        args: arguments
                    }
                ]
            }
        ),
        headers: {
            "Content-type": "application/json"
        }
    })

}

function initializeButtons() { // when the page has loaded
    let elements = document.getElementById("commands").children; // get all buttons with the class
    for (let i = 0; i < elements.length; i++) { // newer browsers can use forEach
        if (elements[i].tagName == "BUTTON"){
            //elements[i].onclick = command //ehhhh may run on assignment which I don't want
            //console.log("Assigned functon: " + i)
        }
    }

    console.log("INITIALIZED BUTTONS")
}

//document.onload = initializeButtons()