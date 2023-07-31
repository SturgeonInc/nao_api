from flask import Flask, json, request
from flask_restful import Resource, Api, reqparse
import ast
import math
from naoqi import ALProxy

app = Flask(__name__)
api = Api(app)

DEFAULT_ROBOT_IP = "127.0.0.1"
DEFAULT_PORT = 9559
DEFAULT_SPEED = 0.5
robot_ip = DEFAULT_ROBOT_IP
robot_port = DEFAULT_PORT

def sayText(args, ip, port):
    tts = ALProxy("ALTextToSpeech", ip, port)
    tts.say(str(args[0]))

def lookInDirection(args, ip, port):
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

def pointAt(args, ip, port):
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

    limb_multiplier = 1
    if arm == "both":
        limb_multiplier = 2

    for i in range(len(angles)):
        angles[i] = math.radians(angles[i])
    
    motion = ALProxy("ALMotion", ip, port)
    motion.setAngles(joints, angles*limb_multiplier, DEFAULT_SPEED)
    motion.setStiffnesses(joints, 1.0)

ACTIONS = {
    u"SayText" : sayText,
    u"PointAt" : pointAt,
    u"LookInDirection" : lookInDirection
}

class Connect_Endpoint(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("ip", required = True, help = "Robot ip address")
        parser.add_argument("port", required = False, help = "Robot port number")
        args = parser.parse_args()

        robot_ip = args["ip"]
        robot_port = args["port"]


class Command_Endpoint(Resource):
    def post(self):
        if request.headers["Content-Type"] != "application/json":
            return {"message" : "command(s) failed: expected JSON"}, 400

        data = request.get_json()
        actionList = data["actionList"]
        print(actionList)

        for action in actionList:
            ACTIONS[action["name"]](action["args"], robot_ip, robot_port)
        
        return {"message" : "Enacted command chain"}, 200
    

api.add_resource(Command_Endpoint, "/api/behavior")
api.add_resource(Connect_Endpoint, "/api/connect")


if __name__ == "__main__":
    app.run()  # run our Flask app