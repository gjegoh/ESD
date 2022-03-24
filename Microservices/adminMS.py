import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import hashlib
import jwt

app = Flask(__name__)

CORS(app)

key = os.urandom(12)
app.config['SECRET_KEY'] = key

@app.route('/validateToken', methods=['GET'])
def validateToken():
    token = request.args.get('token')
    try:
        decoded = jwt.decode(
                            token,
                            app.config.get('SECRET_KEY'),
                            algorithms = ["HS256"]
                        )
        return jsonify(
            {
                'status': True,
                'token': decoded
            }
        )
    except jwt.ExpiredSignatureError:
        return jsonify(
            {
                'status': False,
                'error': 'Signature expired. Please log in again.'
            }
        )
    except jwt.InvalidTokenError:
        return jsonify(
            {
            'status': False,
            'error': 'Invalid token. Please log in again.'
            }
        )
    
@app.route('/adminLogin', methods=['GET'])
def adminLogin():
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            email = request.args.get('email')
            password = request.args.get('pass')
            sql = "USE tutorDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT password FROM tutor WHERE email='{email}' AND isAdmin=1".format(email=email)
            cursor.execute(sql)
            results = cursor.fetchall()
            if (len(results) > 0):
                get_salt = results[0]['password'][:32]
                get_key = results[0]['password'][32:]
                new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), get_salt, 100000)
                if (new_key == get_key): 
                    payload =   {
                        "exp": datetime.utcnow() + timedelta(minutes = 5),
                        "isAdmin": True
                    }
                    token = jwt.encode(
                        payload,
                        app.config.get('SECRET_KEY'),
                        algorithm = "HS256"
                    )
                    return jsonify(
                        {   
                            'token': token,
                            'status': True
                        }
                    )
                else:
                    return jsonify(
                        {   
                            'status': False
                        }
                    )
            else:
                return jsonify(
                        {   
                            'status': False
                        }
                    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)