from flask_jsonschema_validator import JSONSchemaValidator
from flask import Flask, jsonify, request,Response
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import jsonschema

app = Flask(__name__)
api = Api(app)
JSONSchemaValidator(app=app, root="schemas")

app.config["users_schema"] = ""

client = MongoClient("mongodb://35.196.137.199:27017")
db = client.walledDB
users = db["Users"]

def userExist(firstName):
    if users.find({"firstName": firstName}).count() == 0:
        return False
    else:
        return True

class Index(Resource):
    def get(self):
        return "Landed on Index"

class CreateWalletUser(Resource):

    @app.errorhandler(jsonschema.ValidationError)
    def onValidationError(e):
        return Response("There was a validation error: " + str(e), 400)

    @app.route('/register1', methods=['POST'])
    @app.validate('users', 'user_schema')
    def post(self):
        # Get posted data from request
        data = request.get_json()

        # todo - validations here.
        # todo - check access key and secret here

        # get data from payload
        lastName = data["lastName"]
        firstName = data["firstName"]
        address = data["address"]
        email = data["email"]
        phoneNumber = data["phoneNumber"]
        language = data["language"]
        walletOrganizations = data["walletOrganizations"]

        # check if user exists
        if userExist(firstName):
            retJson = {
                "status": 301,
                "msg": "User Already Exists"
            }
            return jsonify(retJson)

        # Insert record
        users.insert({
            "lastName": lastName,
            "firstName": firstName,
            "address": address,
            "email": email,
            "phoneNumber": phoneNumber,
            "language": language,
            "walletOrganizations": walletOrganizations
        })

        # Return successful result
        retJosn = {
            "status": "success",
            "data": {
                    "walletAccountUser": data
                   }
        }
        return jsonify(retJosn)


api.add_resource(Index, '/')
api.add_resource(CreateWalletUser, '/v1/users')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8080)
    # app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
