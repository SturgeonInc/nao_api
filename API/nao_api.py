from flask import Flask
from flask_restful import Resource, Api, reqparse
import json
import ast
import math
from naoqi import ALProxy

app = Flask(__name__)
api = Api(app)

class sayText(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("text", type=str, required=True, help = "Text to be said")
        parser.add_argument("ip", default = "127.0.0.1", required = False, help = "Robot ip address")
        parser.add_argument("port", default = 9559, required = False, help = "Robot port number")
        args = parser.parse_args()

        tts = ALProxy("ALTextToSpeech", args["ip"], args["port"])
        tts.say(args["text"])

        message = "said: " + args["text"]
        return {"message" : message}, 200
    
class lookInDirection(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("angle", type=float, required=True, help = "Azimuthal angle of head")
        parser.add_argument("ip", default = "127.0.0.1", required = False, help = "Robot ip address")
        parser.add_argument("port", default = 9559, required = False, help = "Robot port number")
        args = parser.parse_args()

        motion = ALProxy("ALMotion", args["ip"], args["port"])

        names = "HeadYaw"
        angles = math.radians(args["angle"])
        fractionMaxSpeed = 0.5
        motion.setAngles(names,angles,fractionMaxSpeed)

        message = "tilted head to face direction: " + str(args["angle"])
        return {"message" : message}, 200

class pointAt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("angle", type=float, required=True, help = "Polar angle of right arm")
        parser.add_argument("ip", default = "127.0.0.1", required = False, help = "Robot ip address")
        parser.add_argument("port", default = 9559, required = False, help = "Robot port number")
        args = parser.parse_args()

        motion = ALProxy("ALMotion", args["ip"], args["port"])

        names = "RShoulderPitch"
        angles = math.radians(args["angle"])
        fractionMaxSpeed = 0.5
        motion.setAngles(names,angles,fractionMaxSpeed)
        motion.setStiffnesses(names, 1.0)

        message = "pointed in direction: " + str(args["angle"])
        return {"message" : message}, 200

class chain(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("text", type=str, required=True, help = "Text to be said")
        parser.add_argument("ip", default = "127.0.0.1", required = False, help = "Robot ip address")
        parser.add_argument("port", default = 9559, required = False, help = "Robot port number")
        args = parser.parse_args()

        tts = ALProxy("ALTextToSpeech", args["ip"], args["port"])
        tts.say(args["text"])

        message = "said: " + args["text"]
        return {"message" : message}, 200
    


api.add_resource(pointAt, "/pointAt")
api.add_resource(sayText, "/sayText")
api.add_resource(lookInDirection, "/lookInDirection")
api.add_resource(chain, "/chain")


if __name__ == "__main__":
    app.run()  # run our Flask app