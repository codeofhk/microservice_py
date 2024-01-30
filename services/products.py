import requests
import os
from flask import Flask,jsonify,request,make_response
import jwt
import json
from functools import wraps
from jwt.exceptions import DecodeError

app = Flask(__name__)
port = int(os.environ.get('PORT',5000))
app.config['SECRET_KEY'] = os.urandom(24)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print(data)
            current_user_id = data['user_id']
        except DecodeError:
            return jsonify({'error': 'Authorization token is invalid'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated


@app.route("/")
def home():
	return "hello, welcome to hk's microservices"


with open('users.json','r') as f:
      data = json.load(f)
@app.route('/auth',methods=['POST'])
def authentication():
    if request.headers['content-type'] != 'application/json':
        return jsonify({'error': 'unsupported media type'}) , 415
    username = request.json.get('username')
    password = request.json.get('password')

    for user in data:
        if user['username']==username and user['password']==password:
            token = jwt.encode({'user_id':username,'password':password},app.config['SECRET_KEY'],algorithm='HS256')
            response = make_response(jsonify({'message':'authentication successfull'}))
            response.set_cookie('token',token)
            return response,200
    return jsonify({'error':'username or password wrong check ones'}), 401
          

BASE_URL = "https://dummyjson.com"
@app.route('/products', methods=['GET'])
@token_required
def get_products(current_user_id):
    headers = {'Authorization': f'Bearer {request.cookies.get("token")}'}    
    response = requests.get(f"{BASE_URL}/products", headers=headers)
    if response.status_code != 200:
        return jsonify({'error': response.json()['message']}), response.status_code
    products = []
    for product in response.json()['products']:
        product_data = {
            'id': product['id'],
            'title': product['title'],
            'brand': product['brand'],
            'price': product['price'],
            'description': product['description']
        }
        products.append(product_data)
    return jsonify({'data': products}), 200 if products else 204


if __name__ == "__main__":
 	app.run(debug=True, host="0.0.0,0", port = port)
