from flask import Flask, request, make_response
from flask_restful import Resource, Api, reqparse
import math, time, atexit
from naoqi import ALProxy

app = Flask(__name__)
api = Api(app)

DEFAULT_ROBOT_IP = "127.0.0.1"
DEFAULT_PORT = 9559
DEFAULT_SPEED = 0.2

connected_to_robot = False

# These are the variables that get used in function calls
robot_ip = DEFAULT_ROBOT_IP
robot_port = DEFAULT_PORT

# Args should contain 1 argument: a string of text for the robot to speak
def sayText(args, ip, port):
    tts = ALProxy("ALTextToSpeech", ip, port)
    tts.say(str(args[0]))


# for lookInDirection; elements of the form [headYaw angle, headPitch angle]
# with positive yaw being CCW and pitch being angle of depression from the horizon
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

# Args should contain 1 argument: a string describing a direction to look.
# valid strings are listed in the LOOK_DIRECTIONS dictionary
def lookInDirection(args, ip , port):
    direction = args[0]
    motion = ALProxy("ALMotion", ip, port)

    joints = ["HeadYaw", "HeadPitch"]
    
    # convert angles to radians
    angles = [math.radians(LOOK_DIRECTIONS[direction][0]), math.radians(LOOK_DIRECTIONS[direction][1])]

    # move head
    motion.setAngles(joints, angles, DEFAULT_SPEED)


# for pointAt; elements are of the form [ShoulderRoll angle, ShoulderPitch angle]
# with postitive roll being CCW and pitch being angle of depression from the horizon
ARM_DIRECTIONS = {
    u"upperLeft" : [30,-20],
    u"upwards" : [-13.9,-20],
    u"upperRight" : [-30,-20],
    u"left" : [30,20],
    u"straightOut" : [-13.9,20],
    u"right" : [-30,20],
    u"lowerLeft" : [30,60],
    u"downwards" : [-13.9,60],
    u"lowerRight" : [-30,60],
    u"default" : [-13.9,81.6]
}
# for pointAt; joint groups for naoqi
ARM_JOINTS = {
    u"right" : ["RShoulderRoll", "RShoulderPitch"],
    u"left" : ["LShoulderRoll", "LShoulderPitch"],
    u"both" : ["RShoulderRoll", "RShoulderPitch", "LShoulderRoll", "LShoulderPitch"]
}

# Args should contain 2 arguments: 2 strings, the first being a direction for the robot to point
# (see ARM_DIRECTIONS for a valid direction)
# and the second being the arm the robot should use: left, right, or both
def pointAt(args, ip, port):
    direction = args[0]
    arm = args[1]
    joints = ARM_JOINTS[arm]
    motion = ALProxy("ALMotion", ip, port)
    
    # shallow copy of the list the only way that seems to work
    angles = [ARM_DIRECTIONS[direction][i] for i in range(len(ARM_DIRECTIONS[direction]))]

    # handles adding additional angles if both arms are active
    # and reflecting the left shoulderRoll angle if necessary
    # (the default, "straight out" angle for left shoulder roll is -13.9, vs 13.9 for the right)
    if arm in ["left", "both"]:
        angles_left = list(angles)

        if direction in ["upwards", "straightOut", "downwards", "default"]:
            angles_left[0] *= -1

        if arm == "left":
            angles = angles_left
        else:
            angles += angles_left

    # convert angles to radians
    for i in range(len(angles)):
        angles[i] = math.radians(angles[i])

    # move arm(s)
    motion.setAngles(joints, angles, DEFAULT_SPEED)
    motion.setStiffnesses(joints, 1.0)


# Args should contain 1 argument: a string containing an int (e.g. "200")
# representing a number of milliseconds for the robot to pause between actions
def pause(args, ip, port):
    motion = ALProxy("ALMotion", ip, port)
    motion.stopMove()
    time.sleep(int(args[0])/1000.0)


# Intentionally does nothing in the current implementation
def tiltHead(args, ip, port):
    pass


# for setEyes; elements of the form [red intensity, blue instensity, green instensity]
EMOTIONS = {
    u"happy" : [0.5,0,0],
    u"confused" : [0,1,1],
    u"thinking" : [1,1,0,],
    u"scared" : [1,0,0],
    u"terrified" : [1,0,0],
    u"love" : [0.2,0,0],
    u"looking" : [0,1,0],
    u"default" : "default",
}

# Args should contain 1 argument: a string representing the emotion the robot will
# attempt to emulate by changing the color of its eyes
# A full list of emotions that are supported can be found in the EMOTIONS dict
def setEyes(args, ip, port):
    leds = ALProxy("ALLeds", ip, port)

    EYE_LEDS_RED = [
    "RightFaceLedsRed",
    "LeftFaceLedsRed"
    ]
    EYE_LEDS_GREEN = [
        "RightFaceLedsGreen",
        "LeftFaceLedsGreen"
    ]
    EYE_LEDS_BLUE = [
        "RightFaceLedsBlue",
        "LeftFaceLedsBlue"
    ]

    leds.createGroup("eyesRed",EYE_LEDS_RED)
    leds.createGroup("eyesGreen",EYE_LEDS_GREEN)
    leds.createGroup("eyesBlue",EYE_LEDS_BLUE)
    
    COLOR_GROUPS = ["eyesRed", "eyesGreen", "eyesBlue"]
    if EMOTIONS[args[0]] == "default":
        leds.reset("FaceLeds")
        return

    for i in range(3):
        leds.setIntensity(COLOR_GROUPS[i], EMOTIONS[args[0]][i])
    

# this dict must come after all the functions contained within it
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

    @staticmethod
    def disconnect():
        if not connected_to_robot:
            return
        
        # reset chest led from blue to normal to indicate API server has disconnected
        leds = ALProxy("ALLeds", robot_ip, robot_port)
        leds.reset("ChestLeds")

        # resume background movement
        al = ALProxy("ALAutonomousLife", robot_ip, robot_port)
        al.setAutonomousAbilityEnabled("All", True)

        print("API: DISCONNECTING")

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("ip", required = True, type = str, help = "Robot ip address")
        parser.add_argument("port", required = False, default = 9559, type = int, help = "Robot port number")
        args = parser.parse_args()

        # test connection and turn robot chest LED blue and autonomousLife off if successful
        leds = ALProxy("ALLeds", args["ip"], args["port"])
        leds.setIntensity("ChestLedsBlue", 1)
        al = ALProxy("ALAutonomousLife", robot_ip, robot_port)
        al.setAutonomousAbilityEnabled("All", False)
        
        global robot_ip
        global robot_port
        global connected_to_robot

        robot_ip = args["ip"]
        robot_port= args["port"]
        connected_to_robot = True

        print("API: CONFIGURED CONNECTION")
        print("...Target IP set to: " + robot_ip)
        print("...Target PORT set to: " + str(robot_port))


        return Endpoint.respond({"message" : "Connected to " + robot_ip + ":" + str(robot_port)}, 200)
        
class Command_Endpoint(Endpoint):
    def post(self):
        if request.headers["Content-Type"] != "application/json": # type: ignore
            return Endpoint.respond({"message" : "command(s) failed: expected JSON"}, 400)

        data = request.get_json() # type: ignore
        actionList = data["actionList"]

        if not connected_to_robot:
            return Endpoint.respond({"message" : "Unable to enact command chain - not connected to robot"})

        print("API: ENACTING COMMAND CHAIN")
        print("...Target IP: " + robot_ip)
        print("...Target PORT: " + str(robot_port))
        print("...ActionList JSON data:")
        print("....." + str(actionList))

        

        # use the corresponding functions in the ACTION dict to make robot take *do* stuff
        for action in actionList:
            ACTIONS[action["name"]](action["args"], robot_ip, robot_port)

        return Endpoint.respond({"message" : "Enacted command chain"}, 200)
    

api.add_resource(Command_Endpoint, "/api/behavior")
api.add_resource(Connect_Endpoint, "/api/connect")

# on server stop run the Connect Endpoint's disconnect function, which resets the chest LED
atexit.register(Connect_Endpoint.disconnect)

if __name__ == "__main__":
    app.run()  # run our Flask app