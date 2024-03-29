var api_address, robot_ip, port
const DEFAULT_IP = "192.168.1.3"
const DEFAULT_PORT = 9559
const DEFAULT_API = "http://127.0.0.1:5000/api"

function $(elementID) {
    return document.getElementById(elementID)
}

/** updates robot ip and port API-side based on what's in the textboxes under the CONNECT heading 
 * 
*/
async function connect() {
    robot_ip = $("robot_ip").value
    port = DEFAULT_PORT
    api_address = $("api_address").value

    $("connection_status").innerHTML = "CONNECTION STATUS: ..."

    // check if default values are being for robot ip, port, and api address
    if (api_address == "") api_address = DEFAULT_API

    if (robot_ip == "") robot_ip = DEFAULT_IP
    // check and parse port if is included in ip textbox
    else if (robot_ip.indexOf(":") != -1) {
        port = robot_ip.slice(robot_ip.indexOf(":") + 1, robot_ip.length)
        robot_ip = robot_ip.slice(0, robot_ip.indexOf(":"))
    }

    // update robot ip and port API-side
    try {
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
            // await response and show it in CONNECTION STATUS header
            .then(response => response.json())
            .then(json => $("connection_status").innerHTML = "CONNECTION STATUS: " + json["message"])
            .catch(response => {
                $("connection_status").innerHTML = "CONNECTION STATUS: " + response
                console.error(response)
            })

    }
    catch (error) {
        $("connection_status").innerHTML = "CONNECTION STATUS: " + error
    }

}

/** creates a POST request meant to be sent to the API with the provided actionList.
 * actionList should be of the form:
 *     [
 *         {
 *             name: commandName1,
 *             args: arguments1
 *         },
 *         {
 *             name: commandName2,
 *             args: arguments2
 *         },
 *         .
 *         .
 *         .
 *         et-cetera
 *     ] 
*/
function buildCommandRequest(actionList) {
    return {
        method: "POST",
        body: JSON.stringify(
            {
                intent: "default intent",
                description: "default description",
                actionList: actionList
            }
        ),
        headers: {
            "Content-type": "application/json"
        }
    }
}

/** based on the action button pressed, sends a command to the API server 
 *   telling it what action the robot should do 
*/
function enactCommandOnButtonPress(elementID) {
    let commandName, arguments
    commandName = elementID.slice(0, elementID.indexOf(":"))

    console.log("Enacting: " + elementID)

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

    // generate POST request with ActionScript JSON
    let commandReq = buildCommandRequest([
        {
            name: commandName,
            args: arguments
        }
    ])

    // send request commandReq to address api_address/behavior
    fetch(api_address + "/behavior", commandReq)
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
                        name: "Pause",
                        args: ["300"]
                    },
                    {
                        name: "LookInDirection",
                        args: ["down"]
                    },
                    {
                        name: "Pause",
                        args: ["300"]
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
                        name: "Pause",
                        args: ["300"]
                    },
                    {
                        name: "LookInDirection",
                        args: ["right"]
                    },
                    {
                        name: "Pause",
                        args: ["300"]
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

// enacts welcome Action Sequence
function welcome() {
    fetch(api_address + "/behavior", {
        method: "POST",
        body: JSON.stringify(
            {
                intent: "default intent",
                description: "default description",
                actionList: [
                    // hit upper right pose
                    {
                        name: "LookInDirection",
                        args: ["upperRight"]
                    },
                    {
                        name: "SetEyes",
                        args: ["looking"]
                    },
                    {
                        name: "Pause",
                        args: ["1000"]
                    },

                    //hit lower left pose
                    {
                        name: "LookInDirection",
                        args: ["center"]
                    },
                    {
                        name: "Pause",
                        args: ["1000"]
                    },

                    //resume default pose
                    {
                        name: "SayText",
                        args: ["welcome!"]
                    },
                    {
                        name: "Pause",
                        args: ["1000"]
                    },
                    {
                        name: "SetEyes",
                        args: ["default"]
                    }

                ]
            }
        ),
        headers: {
            "Content-type": "application/json"
        }
    })
}
