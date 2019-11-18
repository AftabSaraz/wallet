from flask_jsonschema_validator import JSONSchemaValidator
from flask import Flask, jsonify, request, Response
from flask_restful import Resource
from pymongo import MongoClient
import bcrypt
import jsonschema
from bson.json_util import dumps
from bson import ObjectId
from custom_error_handler import CustomErrorHandler


app = Flask(__name__)
JSONSchemaValidator(app=app, root="schemas")
app.config['TRAP_HTTP_EXCEPTIONS'] = True     # https://stackoverflow.com/a/33711404/2493079
app.url_map.strict_slashes = False  # https://stackoverflow.com/a/40365514/2493079

# todo move database credentials to secrets and fetch from there.
client = MongoClient("mongodb://35.196.137.199:27017")
db = client.walledDB
users = db["Users"]


def response_generator(status, data):
    retJson = {
            "status": status,
            "data": data
        }
    return dumps(retJson)


@app.route('/', methods=['GET'])
def get():
    raise CustomErrorHandler('The client does not have permission to access this resource', 403, 'error')


@app.route('/v1/create_user', methods=['POST'])
@app.validate('user', 'user_schema')
def create_user():

    data = request.get_json()

    # todo - check access key and secret here

    # get data from payload
    lastName = data["lastName"]
    firstName = data["firstName"]
    address = data["address"]
    email = data["email"]
    phoneNumber = data["phoneNumber"]
    language = data["language"]
    walletOrganizations = data["walletOrganizations"]

    # Insert wallet account user into db
    user_id = users.insert({
        "lastName": lastName,
        "firstName": firstName,
        "address": address,
        "email": email,
        "phoneNumber": phoneNumber,
        "language": language,
        "walletOrganizations": walletOrganizations
    })

    if user_id is not None:
        data.update({"id": str(user_id)})
        retJson = {
            "status": "success",
            "data": {
                "walletAccountUser": data
            }
        }
        return response_generator('success', data)
    else:
        raise CustomErrorHandler("Can't create the wallet account user", 4010, 'error')


@app.route('/v1/update_user/<string:user_id>', methods=['PATCH'])
@app.validate('user', 'user_schema')
def update_user(user_id):

    objId = ObjectId(user_id)
    data = request.get_json()

    # todo - check access key and secret here

    # get data from payload
    lastName = data["lastName"]
    firstName = data["firstName"]
    address = data["address"]
    email = data["email"]
    phoneNumber = data["phoneNumber"]
    language = data["language"]
    walletOrganizations = data["walletOrganizations"]

    # check if the user with provided ID exists
    user_data = fetch_user_data(user_id)
    if user_data is not None:
        # Insert record
        user_id = users.update(
            {"_id": objId},
            {"$set": {
                        "lastName": lastName,
                        "firstName": firstName,
                        "address": address,
                        "email": email,
                        "phoneNumber": phoneNumber,
                        "language": language,
                        "walletOrganizations": walletOrganizations
                    }})
        if user_id is not None:
            # Return successful result
            data.update({"id": str(user_id)})
            return response_generator('success', data)
        else:
            raise CustomErrorHandler('Unable to update wallet account user information', 4040, 'error')
    else:
        raise CustomErrorHandler('Wallet account user not found', 4020, 'error')


@app.route('/v1/users/', methods=['GET'])
def obtain_wallet_account_users():
    user_data = users.find()
    if user_data.count != 0:
        return response_generator('success', user_data)
    else:
        raise CustomErrorHandler("Wallet account user not found", 4020, 'error')


@app.route('/v1/users/<string:user_id>', methods=['GET'])
def fetch_user_data(user_id):
    if user_id is not None:
        objId = ObjectId(user_id)
        user_data = users.find({
            "_id": objId
        })
    else:
        raise CustomErrorHandler('Missing user_id parameter', 401, 'error')

    if user_data.count() != 0:
        return response_generator('success', user_data)
    else:
        raise CustomErrorHandler("Can't obtain wallet account user data", 4030, 'error')


# custom error handler
@app.errorhandler(CustomErrorHandler)
def custom_error_handler(error):
    response = jsonify(error.create_response())
    response.status_code = error.status_code
    return response

# custom error response on 404
@app.errorhandler(404)
def resource_not_found(e):
    retJson = {
        "status": 'fail',
        "statusCode": e.code,
        "statusDescription": "Resource not found"
    }
    return jsonify(retJson)

# custom error response on 404
@app.errorhandler(405)
def method_not_supported(error):
    retJson = {
        "status": 'fail',
        "statusCode": error.code,
        "statusDescription": "Method not supported"
    }
    return jsonify(retJson)

# custom error handler for JSON schema validation
@app.errorhandler(jsonschema.ValidationError)
def resource_not_found(error):
    retJosn = {
        "status": 400,
        "data": error.message
    }
    return jsonify(retJosn)



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8088)
    # app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
