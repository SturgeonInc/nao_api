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

function shakeHeadYes(){
    fetch(api_address+"/behavior", {
        method: "POST",
        body: JSON.stringify(
            {
                intent: "default intent",
                description: "default description",
                actionList: [
                    {
                        name: "LookInDirection",
                        args: ["up"]
                    },
                    {
                        name: "LookInDirection",
                        args: ["down"]
                    },
                    {
                        name: "LookInDirection",
                        args: ["center"]
                    }
                ]
            }
        ),
        headers: {
            "Content-type": "application/json"
        }
    })
}

function shakeHeadNo(){
    fetch(api_address+"/behavior", {
        method: "POST",
        body: JSON.stringify(
            {
                intent: "default intent",
                description: "default description",
                actionList: [
                    {
                        name: "LookInDirection",
                        args: ["left"]
                    },
                    {
                        name: "LookInDirection",
                        args: ["right"]
                    },
                    {
                        name: "LookInDirection",
                        args: ["center"]
                    }
                ]
            }
        ),
        headers: {
            "Content-type": "application/json"
        }
    })
}

function disco(){
    fetch(api_address+"/behavior", {
        method: "POST",
        body: JSON.stringify(
            {
                intent: "default intent",
                description: "default description",
                actionList: [
                    // hit upper right pose
                    {
                        name: "PointAt",
                        args: ["upperRight", "right"]
                    },
                    {
                        name: "LookInDirection",
                        args: ["upperRight"]
                    },
                    {
                        name: "SetEyes",
                        args: ["confused"]
                    },
                    {
                        name: "Pause",
                        args: ["1000"]
                    },

                    //hit lower left pose
                    {
                        name: "PointAt",
                        args: ["lowerLeft", "left"]
                    },
                    {
                        name: "LookInDirection",
                        args: ["lowerLeft"]
                    },
                    {
                        name: "SetEyes",
                        args: ["terrified"]
                    },
                    {
                        name: "Pause",
                        args: ["3000"]
                    },

                    //resume default pose
                    {
                        name: "SetEyes",
                        args: ["default"]
                    },
                    {
                        name: "LookInDirection",
                        args: ["center"]
                    },
                    {
                        name: "PointAt",
                        args: ["default", "both"]
                    },
                ]
            }
        ),
        headers: {
            "Content-type": "application/json"
        }
    })
}
