from flask import Flask, json, request
from flask_restful import Resource, Api, reqparse
import ast
import math
from naoqi import ALProxy

app = Flask(__name__)
api = Api(app)

DEFAULT_SPEED = 0.5
DEFAULT_ROBOT_IP = "127.0.0.1"
DEFAULT_PORT = 9559

# TODO MAKE FUNCTIONS TAKE DICTIONARIES SO I CAN PLUG AND PLAY IN CHAIN
def sayText(text, ip, port):
    tts = ALProxy("ALTextToSpeech", ip, port)
    tts.say(text)

    message = "said: " + text
    return {"message" : message}, 200

def lookInDirection(angle, speed, ip, port):
    motion = ALProxy("ALMotion", ip, port)
    motion.setAngles("HeadYaw",math.radians(angle),speed)

    message = "tilted head to face direction: " + str(angle)
    return {"message" : message}, 200

def pointAt(angle, speed, ip, port):
    motion = ALProxy("ALMotion", ip, port)
    motion.setAngles("RShoulderPitch", math.radians(angle), speed)
    motion.setStiffnesses("RShoulderPitch", 1.0)

    message = "pointed in direction: " + str(angle)
    return {"message" : message}, 200


commands = {
    "sayText" : sayText,
    "pointAt" : pointAt,
    "lookInDirection" : lookInDirection
}

class sayText_Endpoint(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("text", type=str, required=True, help = "Text to be said")
        parser.add_argument("ip", default = DEFAULT_ROBOT_IP, required = False, help = "Robot ip address")
        parser.add_argument("port", type=int, default = DEFAULT_PORT, required = False, help = "Robot port number")
        args = parser.parse_args()
        
        return sayText(args["text"], args["ip"], args["port"])

        # try:
        #     return sayText(args["text"], args["ip"], args["port"])
        # except:
        #     return {"message" : "An error has occurred"}, 500
    

class lookInDirection_Endpoint(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("angle", type=float, required=True, help = "Azimuthal angle of head")
        parser.add_argument("speed", type=float, default = DEFAULT_SPEED, required = False, help = "Motor speed; 0<=x<=1")
        parser.add_argument("ip", default = DEFAULT_ROBOT_IP, required = False, help = "Robot ip address")
        parser.add_argument("port", type=int, default = DEFAULT_PORT, required = False, help = "Robot port number")
        args = parser.parse_args()
        
        return lookInDirection(args["angle"], args["speed"], args["ip"], args["port"])

class pointAt_Endpoint(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("angle", type=float, required=True, help ="Polar angle of right arm")
        parser.add_argument("speed", type=float, default = DEFAULT_SPEED, required=False, help="Motor speed; 0<=x<=1")
        parser.add_argument("ip", default=DEFAULT_ROBOT_IP, required=False, help="Robot ip address")
        parser.add_argument("port", type=int, default=DEFAULT_PORT, required=False, help="Robot port number")
        args = parser.parse_args()

        return pointAt(args["angle"], args["speed"], args["ip"], args["port"])

        # try:
        #     return pointAt(args["angle"], args["speed"], args["ip"], args["port"])
        # except:
        #     return {"message" : "An error has occurred"}, 500
    

class chain_Endpoint(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("ip", default = "127.0.0.1", required = False, help = "Robot ip address")
        parser.add_argument("port", default = 9559, required = False, help = "Robot port number")
        args = parser.parse_args()

        if request.headers["Content-Type"] != "application/json":
            return {"message" : "command chain failed: expected JSON"}, 400

        data = request.get_json()

        print(data)
        for action in data:
            commands[action["command"]](args["ip"],args["port"])
        


        return {"message" : "Enacted command chain"}, 200
    


api.add_resource(pointAt_Endpoint, "/pointAt")
api.add_resource(sayText_Endpoint, "/sayText")
api.add_resource(lookInDirection_Endpoint, "/lookInDirection")
api.add_resource(chain_Endpoint, "/chain")


if __name__ == "__main__":
    app.run()  # run our Flask app