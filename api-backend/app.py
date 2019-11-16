from flask_jsonschema_validator import JSONSchemaValidator
from flask import Flask, jsonify, request, Response
from flask_restful import Resource
from pymongo import MongoClient
import bcrypt
import jsonschema
from bson.json_util import dumps
from bson import ObjectId

app = Flask(__name__)
JSONSchemaValidator(app=app, root="schemas")

client = MongoClient("mongodb://35.196.137.199:27017")
db = client.walledDB
users = db["Users"]


def userExist(firstName):
    if users.find({"firstName": firstName}).count() == 0:
        return False
    else:
        return True


@app.route('/', methods=['GET'])
def get():
    return "Landed on Index"


@app.route('/create_user', methods=['POST'])
@app.validate('user', 'user_schema')
def post():
    # Get posted data from request
    data = request.get_json()
    print(data)
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
    user_id = users.insert({
        "lastName": lastName,
        "firstName": firstName,
        "address": address,
        "email": email,
        "phoneNumber": phoneNumber,
        "language": language,
        "walletOrganizations": walletOrganizations
    })

    # Return successful result
    data.update({"id": str(user_id)})
    retJosn = {
        "status": "success",
        "data": {
            "walletAccountUser": data
        }
    }
    return jsonify(retJosn)


def fetchUser(user_id):
    objId = ObjectId(user_id)
    return users.find({
        "_id": objId
    })


def fetchAllUsers():
    return users.find()


@app.route('/v1/users', methods=['GET'])
def retrieveUser():

    user_id = request.args.get('user_id')

    if user_id is None:
        user_data = fetchAllUsers()
    else:
        user_data = fetchUser(user_id)

    # Build successful response
    retJson = {
        "status": 200,
        "data": user_data
    }

    return dumps(retJson)


@app.errorhandler(jsonschema.ValidationError)
def onValidationError(e):
    return Response("There was a validation error: " + str(e), 400)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8088)
    # app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
