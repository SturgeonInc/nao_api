from flask import Flask, request, make_response
from flask_restful import Resource, Api, reqparse
import math
import time
from naoqi import ALProxy

app = Flask(__name__)
api = Api(app)

DEFAULT_ROBOT_IP = "127.0.0.1"
DEFAULT_PORT = 9559
DEFAULT_SPEED = 0.5

# These are the variables that get used in function calls
robot_ip = DEFAULT_ROBOT_IP
robot_port = DEFAULT_PORT

# Args should contain 1 argument: a string of text for the robot to speak
def sayText(args, ip, port):
    tts = ALProxy("ALTextToSpeech", ip, port)
    print(str(args[0]))
    tts.say(str(args[0]))

# Args should contain 1 argument: a string describing a direction to look.
# valid strings are listed in the LOOK_DIRECTIONS dictionary
def lookInDirection(args, ip, port):
    
    # u-strings because that's what JSONs give and there is no implicit conversion
    # these lists are of the form [headYaw angle, headPitch angle]
    # positive yaw being counter-clockwise and postitive pitch being down
    LOOK_DIRECTIONS = {
        u"upperLeft" : [30,-25],
        u"up" : [0,-25],
        u"upperRight" : [-30,-25],
        u"left" : [30,0],
        u"center" : [0,0],
        u"right" : [-30,0],
        u"lowerLeft" : [30,25],
        u"down" : [0,25],
        u"lowerRight" : [-30,25],
    }

    direction = args[0]

    # error to send back to the user later
    if not direction in LOOK_DIRECTIONS:
        return """No direction argument detected - must be one of: 
            upperLeft
            up
            upperRight
            left
            center
            right
            lowerLeft
            down
            lowerRight
        """

    motion = ALProxy("ALMotion", ip, port)
    joints = ["HeadYaw", "HeadPitch"]
    angles = [math.radians(LOOK_DIRECTIONS[direction][0]), math.radians(LOOK_DIRECTIONS[direction][1])]
    motion.setAngles(joints, angles, DEFAULT_SPEED)

# Args should contain 2 arguments: 2 strings, the first being a direction for the robot to point
# (see ARM_DIRECTIONS for a valid direction)
# and the second being the arm the robot should use: left, right, or both
def pointAt(args, ip, port):
    # these lists are of the form [ShoulderRoll angle, ShoulderPitch angle]
    # positive roll being counter-clockwise and postitive pitch being down
    ARM_DIRECTIONS = {
        u"upperLeft" : [30,-20],
        u"upwards" : [-12.7,-20],
        u"upperRight" : [-30,-20],
        u"left" : [30,20],
        u"straightOut" : [-12.7,20],
        u"right" : [-30,20],
        u"lowerLeft" : [30,60],
        u"downwards" : [-12.7,60],
        u"lowerRight" : [-30,60],
        u"default" : [-12.7,83.1]
    }

    ARM_JOINTS = {
        u"right" : ["RShoulderRoll", "RShoulderPitch"],
        u"left" : ["LShoulderRoll", "LShoulderPitch"],
        u"both" : ["RShoulderRoll", "RShoulderPitch", "LShoulderRoll", "LShoulderPitch"]
    }

    direction = args[0]
    arm = args[1]

    # errors to send back to the user later
    if not direction in ARM_DIRECTIONS:
        return """No direction argument detected - must be one of: 
            upperLeft
            upwards
            upperRight
            left
            straightOut
            right
            lowerLeft
            downwards
            lowerRight
            default
        """
    if not arm in ARM_JOINTS:
        return """No arm argument detected - must be one of: 
            left
            right
            both
        """
    
    joints = ARM_JOINTS[arm]
    angles = ARM_DIRECTIONS[direction]

    # this is here because we need to have an angle for each arm's joints
    # so when both arms are active, we need the angles list, but twice
    # I can't modify the angles list due to it being a deep copy of an immutable dict
    # You can't even .copy() or list() it, so we append it to itself as we pass it into setAngles
    limb_multiplier = 1
    if arm == "both":
        limb_multiplier = 2

    for i in range(len(angles)):
        angles[i] = math.radians(angles[i])
    
    motion = ALProxy("ALMotion", ip, port)
    motion.setAngles(joints, angles*limb_multiplier, DEFAULT_SPEED)
    motion.setStiffnesses(joints, 1.0)

# Args should contain 1 argument: a string containing an int (e.g. "200")
# representing a number of milliseconds for the robot to pause between actions
def pause(args, ip, port):
    motion = ALProxy("ALMotion", ip, port)
    motion.stopMove()
    #motion.stiffness("body", 1.0)
    time.sleep(int(args[0])/1000.0)

# Intentionally does nothing in the current implementation
def tiltHead(args, ip, port):
    pass

# Args should contain 1 argument: a string representing the emotion the robot will
# attempt to emulate by changing the color of its eyes
# Currently, "scared" or "terrified" yields red eyes, "confused" yields blue eyes 
# All other values can result in the robot using the standard light color for the eyes
# A full list of emotions that intend(?) to be supported can be found in the EMOTIONS dict
def setEyes(args, ip, port):
    EMOTIONS = {
        u"happy" : "default",
        u"confused" : [0,0,1],
        u"thinking" : "default",
        u"scared" : [1,0,0],
        u"terrified" : [1,0,0],
        u"love" : "default",
        u"looking" : "default",
        u"default" : "default",
    }

    if not args[0] in EMOTIONS:
        return """Emotion not recognized. Must be one of:
            happy
            confused
            thinking
            scared
            terrified
            love
            looking
            default
        """
 
    leds = ALProxy("ALLeds", ip, port)

    red = [
    "RightFaceLedsRed",
    "LeftFaceLedsRed"
    ]
    green = [
        "RightFaceLedsGreen",
        "LeftFaceLedsGreen"
    ]
    blue = [
        "RightFaceLedsBlue",
        "LeftFaceLedsBlue"
    ]

    leds.createGroup("eyesRed",red)
    leds.createGroup("eyesGreen",green)
    leds.createGroup("eyesBlue",blue)
    
    COLOR_GROUPS = ["eyesRed", "eyesGreen", "eyesBlue"]
    if EMOTIONS[args[0]] == "default":
        leds.reset("FaceLeds")
        return

    for i in range(3):
        leds.setIntensity(COLOR_GROUPS[i], EMOTIONS[args[0]][i])
    


ACTIONS = {
    u"SayText" : sayText,
    u"PointAt" : pointAt,
    u"LookInDirection" : lookInDirection,
    u"Pause" : pause,
    u"TiltHead" : tiltHead,
    u"SetEyes" : setEyes
}

class Endpoint(Resource):
    @staticmethod
    def respond(*args):
        response = make_response(*args)
        response.headers.add("Access-Control-Allow-Origin", "null")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
    def options(self):
        return Endpoint.respond()

class Connect_Endpoint(Endpoint):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("ip", required = True, help = "Robot ip address")
        parser.add_argument("port", required = False, default = 9559, help = "Robot port number")
        args = parser.parse_args()

        global robot_ip
        global robot_port
        robot_ip = str(args["ip"])
        robot_port= int(args["port"])
        print("IP: " + robot_ip)
        print("PORT: " + str(robot_port))

        return Endpoint.respond({"message" : "Connected"}, 200)
        
class Command_Endpoint(Endpoint):
    def post(self):
        if request.headers["Content-Type"] != "application/json":
            return Endpoint.respond({"message" : "command(s) failed: expected JSON"}, 400)

        data = request.get_json()
        actionList = data["actionList"]
        print(robot_ip)
        print(robot_port)
        print(actionList)

        for action in actionList:
            ACTIONS[action["name"]](action["args"], robot_ip, robot_port)

        return Endpoint.respond({"message" : "Enacted Chain"}, 200)
    

api.add_resource(Command_Endpoint, "/api/behavior")
api.add_resource(Connect_Endpoint, "/api/connect")


if __name__ == "__main__":
    app.run()  # run our Flask app