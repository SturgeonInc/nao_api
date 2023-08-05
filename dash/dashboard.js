var api_address, robot_ip, port
const DEFAULT_IP = "192.168.1.3"
const DEFAULT_PORT = 9559
const DEFAULT_API = "http://127.0.0.1:5000/api"

function $(elementID) {
    return document.getElementById(elementID)
}

// updates robot ip and port API-side based on what's in the textboxes under the CONNECT heading
function connect() {
    robot_ip = $("robot_ip").value
    port = DEFAULT_PORT
    api_address = $("api_address").value

    // check if default values are being for robot ip, port, and api address
    if (api_address == "") api_address = DEFAULT_API

    if (robot_ip == "") robot_ip = DEFAULT_IP
    // check and parse port if is included in ip textbox
    else if (robot_ip.indexOf(":") != -1) {
        port = robot_ip.slice(robot_ip.indexOf(":") + 1, robot_ip.length)
        robot_ip = robot_ip.slice(0, robot_ip.indexOf(":"))
    }

    // update robot ip and port API-side
    fetch(api_address + "/connect", {
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

// based on the action button pressed, sends a command to the API server 
// telling it what action the robot should do
function enactCommand(elementID) {
    let commandName, arguments
    commandName = elementID.slice(0, elementID.indexOf(":"))

    console.log(elementID)

    // check if elementID has arguments in it, and if so include them
    // (commands with no args or args that aren't stored in their element ID
    // have a trailing ":" in their ID e.g. "SayText:")
    if (elementID.indexOf(":") != elementID.length) {
        arguments = [elementID.slice(elementID.indexOf(":") + 1)]
    }

    // get SayText args from textbox
    if (commandName == "SayText") arguments = [$("say_text_textbox").value]
    // determine PointAt arm args from checkboxes
    else if (commandName == "PointAt") {
        let left = $("left_arm").checked, right = $("right_arm").checked

        if (left && right) arguments.push("both")
        else if (left) arguments.push("left")
        else arguments.push("right") // if neither box is checked, right arm will be used
    }

    // send JSON with appropriate action & args to API server
    fetch(api_address + "/behavior", {
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

// enacts shakeHeadYes Action Sequence
function shakeHeadYes() {
    fetch(api_address + "/behavior", {
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

// enacts shakeHeadNo Action Sequence
function shakeHeadNo() {
    fetch(api_address + "/behavior", {
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

// enacts disco Action Sequence
function disco() {
    fetch(api_address + "/behavior", {
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
