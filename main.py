import pymysql
from app import app
from MySqlConnection import mydb
from flask import Flask, request, jsonify, json, redirect, url_for
#from werkzeug import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
import jwt
import datetime

CORS(app)

app.config['SECRET_KEY'] = 'James!1@2'

SocketIo = SocketIO(app,cors_allowed_origins="*")

app.host = 'localhost'


#app.debug = True

@SocketIo.on("send-msg")
def handleMithhu(*msg):
    print(type(msg[0]),'show-msg',msg)
    cursor = mydb.cursor(pymysql.cursors.DictCursor)
    sqlQuery = "INSERT INTO chathistory (toId,fromId,message) VALUES (%s,%s,%s)"
    values = (msg[0]['toId'],msg[0]['fromId'],msg[0]['message'])
    cursor.execute(sqlQuery, values )
    mydb.commit()
    emit("show-msg",msg,broadcast=True)
    return msg


@app.route('/signup', methods=['POST'])
def signUpUser():
    try:
        bodyParams = request.get_json()
        print(bodyParams,'bodyParams')
        if request.method == 'POST':
            cursor = mydb.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "INSERT INTO users (name,username,password,mobile,email) VALUES (%s,%s,%s,%s,%s)"
            values = (bodyParams['name'],bodyParams['username'],bodyParams['password'],bodyParams['mobile'],bodyParams['email'])
            cursor.execute(sqlQuery, values )
            mydb.commit()
            resp = jsonify({'result':{'message':'User added successfully','status':0}})
            resp.status_code = 200
            resp.headers={"content-type":"application/json"}
            return resp
        else:
            resp = jsonify({'result':{'message':'Something is not good','status':-1}})
            return resp
    except Exception as e:
        print(e)
        resp = jsonify({'result':{'message':'Something is not good/Exception','status':-1}})
        return resp
    finally:
        cursor.close() 
        #mydb.close()
      
@app.route('/login', methods=['POST'])
def signInUser():
    try:
        bodyParams = request.get_json()
        print(bodyParams,'bodyParams')
        if request.method == 'POST':
            cursor = mydb.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "SELECT * FROM users WHERE username=%s && password = %s"
            values = (bodyParams['username'],bodyParams['password'],)
            cursor.execute(sqlQuery, values )
            rows = cursor.fetchall()
            row_headers=[x[0] for x in cursor.description] 
            json_data = []
            for row in rows:
                json_data.append({
                    row_headers[0]:row[0],
                    row_headers[1]:row[1],
                    row_headers[2]:row[2],
                    row_headers[3]:row[3],
                    row_headers[4]:row[4],
                    row_headers[5]:row[5],
                    row_headers[6]:row[6],
                    row_headers[7]:row[7],
                    row_headers[8]:row[8],
                    row_headers[9]:row[9],
                })
    
            print('json_data',json_data)
            
            if len(rows) == 1:
                token = jwt.encode({'user':json_data[0]['id'],'exp':datetime.datetime.utcnow()+datetime.timedelta(hours=24)},app.config['SECRET_KEY'])
                print(token,'token')               
                resp = jsonify({'result':{'message':'Login successfully','status':0,'data':json_data,'token':str(token.decode('UTF-8'))}})
            else:
                resp = jsonify({'result':{'message':'User not found','status':-1}})
            resp.set_cookie('YourSessionCookie', '1234')
            resp.status_code = 200
            resp.headers={"content-type":"application/json"}
            return resp
        else:
            resp = jsonify({'result':{'message':'Something is not good','status':-1}})
            return resp
    except Exception as e:
        print(e)
        resp = jsonify({'result':{'message':'Something is not good/Exception','status':-1}})
        return resp
    finally:
        cursor.close() 
        #mydb.close()


@app.route('/friendsList')
def friendsList():
    try:
        token = ''
        if request.headers.get('Authorization'):
            token = jwt.decode(request.headers.get('Authorization'),app.config['SECRET_KEY'])
        print(token,'token')
        cursor = mydb.cursor(pymysql.cursors.DictCursor)
        if token:
            print(request.args,request.args.get('id'),'friendsList id')
            cursor.execute("SELECT * FROM friendlist WHERE id=%s",(request.args.get('id'),))
            rows = cursor.fetchall()[0]
            rows = rows[1]
            rows = tuple(json.loads(rows))
            print(rows,'rowwwwwwll')
            if request.args.get('searchFor'):
                query = 'SELECT * FROM users WHERE id IN {} && name LIKE "%{}%" '
            else:
                query = 'SELECT * FROM users WHERE id IN {} '
            print(query.format(rows,request.args.get('searchFor')),'query')
            cursor.execute(query.format(rows,request.args.get('searchFor')))
            rows = cursor.fetchall()
            print(rows,'rowwwwww')
            row_headers=[x[0] for x in cursor.description] 
            json_data = []
            for row in rows:
                json_data.append({
                    row_headers[0]:row[0],
                    row_headers[1]:row[1],
                    row_headers[2]:row[2],
                    row_headers[3]:row[3],
                    row_headers[4]:row[4]
                })
            print(json_data,'json_data')
            resp = jsonify({'result':{'message':'Request successful','status':0,'data':json_data}})
            resp.status_code = 200
            return resp
        else:
            resp = jsonify({'result':{'message':'User not authorized','status':-1}})
            resp.status_code = 200
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
		#mydb.close()
        
@app.route('/getChatHistory')
def getChatHistory():
    try:
        token = ''
        if request.headers.get('Authorization'):
            token = jwt.decode(request.headers.get('Authorization'),app.config['SECRET_KEY'])
        print(token,'token')
        cursor = mydb.cursor(pymysql.cursors.DictCursor)
        if token:
            print(request.args,request.args.get('toId'),'getChatHistory request.args.get()')
    #        cursor = mydb.cursor(pymysql.cursors.DictCursor)
            offset = (int(request.args.get('pageNo')) - 1 ) * int(request.args.get('pageSize'))
            values = (request.args.get('toId'),request.args.get('toId'),request.args.get('fromId'),request.args.get('fromId'),)
            query = "SELECT * FROM chathistory WHERE (toId=%s or fromId=%s) && (fromId=%s or toId=%s)  ORDER BY messageTime "+ "LIMIT "+request.args.get('pageSize')+" OFFSET "+ str(offset)
            print(query,'query')
            cursor.execute(query, values)
            rows = cursor.fetchall()
            print(rows,'getChatHistory rowwwwww')
            row_headers=[x[0] for x in cursor.description] 
            json_data = []
            for row in rows:
                json_data.append({
                    row_headers[0]:row[0],
                    row_headers[1]:row[1],
                    row_headers[2]:row[2],
                    row_headers[3]:row[3],
                })
            print(json_data,'json_data getChatHistory')
            resp = jsonify({'result':{'message':'Request successful','status':0,'data':json_data}})
            resp.status_code = 200
            return resp
        else:
            resp = jsonify({'result':{'message':'User not authorized','status':-1}})
            resp.status_code = 200
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
		#mydb.close()


@app.route('/users')
def users():
    try:
        print(request.args,request.args.get('id'),'request.args.get()')
        cursor = mydb.cursor(pymysql.cursors.DictCursor)
        if request.args.get('searchFor'):
            print('iffff')
            query = 'SELECT * FROM users WHERE id=%s && name LIKE %s'
            cursor.execute(query,(request.args.get('id'), "%"+request.args.get('searchFor')+"%",))
        else:
            print('elsee')
            query = 'SELECT * FROM users WHERE id=%s'
            cursor.execute(query,(request.args.get('id'),))
        rows = cursor.fetchall()
        row_headers=[x[0] for x in cursor.description] 
        json_data = []
        for row in rows:
            json_data.append({
                row_headers[0]:row[0],
                row_headers[1]:row[1],
                row_headers[2]:row[2],
                row_headers[3]:row[3],
                row_headers[4]:row[4],
            })
        resp = jsonify(json_data)
        resp.status_code = 200
        return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
		#mydb.close()
        
@app.route('/getAllusers')
def getAllusers():
    try:
        print(request.headers.get('Authorization'),'request.headers')
        token = ''
        if request.headers.get('Authorization'):
            token = jwt.decode(request.headers.get('Authorization'),app.config['SECRET_KEY'])
        print(token,'token')
        cursor = mydb.cursor(pymysql.cursors.DictCursor)
        if token:
            print(request.args,'request.args.get()')
            if request.args.get('searchFor'):
                print('iffff')
                query = 'SELECT * FROM users WHERE id!=%s && name LIKE %s'
                cursor.execute(query,(request.args.get('id'), "%"+request.args.get('searchFor')+"%",))
            else:
                print('elsee')
                query = 'SELECT * FROM users WHERE id!=%s'
                cursor.execute(query,(request.args.get('id'),))
            rows = cursor.fetchall()
            row_headers=[x[0] for x in cursor.description] 
            json_data = []
            for row in rows:
                json_data.append({
                    row_headers[0]:row[0],
                    row_headers[1]:row[1],
                    row_headers[2]:row[2],
                    row_headers[3]:row[3],
                    row_headers[4]:row[4],
                    row_headers[5]:row[5],
                    row_headers[6]:row[6],
                    row_headers[7]:row[7],
                    row_headers[8]:row[8],
                    row_headers[9]:row[9],
                })
            resp = jsonify({'result':{'message':'Request successful','status':0,'data':json_data}})
            resp.status_code = 200
            return resp
        else:
            resp = jsonify({'result':{'message':'User not authorized','status':-1}})
            resp.status_code = 200
            return resp
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
		#mydb.close()

@app.route('/addUserToFriendList', methods=['POST'])
def addUserToFriendList():
    try:
        bodyParams = request.get_json()
        print(bodyParams,'bodyParams')
        token = ''
        if request.headers.get('Authorization'):
            token = jwt.decode(request.headers.get('Authorization'),app.config['SECRET_KEY'])
        print(token,'token')
        cursor = mydb.cursor(pymysql.cursors.DictCursor)
        if token:
            if request.method == 'POST':
                cursor = mydb.cursor(pymysql.cursors.DictCursor)
                cursor.execute("SELECT * FROM friendlist WHERE id=%s",(bodyParams['id'],))
                rows = cursor.fetchall()
                print(rows,'rowwww')
                if len(rows) > 0:
                    rows = rows[0]  
                    rows = rows[1]
                    rows = json.loads(rows)
                    print(rows,'rowwwwwwll')
                    
                    if bodyParams['friendsId'][0] in rows:
                        print("yess")
                        resp = jsonify({'result':{'message':'User already exist','status':0}})
                    else:
                        print("noooo")
                        rows.append(bodyParams['friendsId'][0])    
                        sqlQuery = "UPDATE friendlist SET friendsId=%s WHERE id=%s"
                        values = (str(rows),bodyParams['id'],)
                        cursor.execute(sqlQuery, values )
                        mydb.commit()
                        resp = jsonify({'result':{'message':'User added successfully','status':0}})
                else: 
                    sqlQuery = "INSERT INTO friendlist (id,friendsId) VALUES (%s,%s)"
                    values = (bodyParams['id'],str(bodyParams['friendsId']),)
                    cursor.execute(sqlQuery, values )
                    mydb.commit()
                    resp = jsonify({'result':{'message':'User added successfully','status':0}})
                
                resp.status_code = 200
                resp.headers={"content-type":"application/json"}
                return resp
            else:
                resp = jsonify({'result':{'message':'Something is not good','status':-1}})
                return resp
        else:
            resp = jsonify({'result':{'message':'User not authorized','status':-1}})
            resp.status_code = 200
            return resp
    except Exception as e:
        print(e)
        resp = jsonify({'result':{'message':'Something is not good/Exception','status':-1}})
        return resp
    finally:
        cursor.close() 
        #mydb.close()

@app.route('/updateUserDetails', methods=['POST'])
def updateUserDetails():
    try:
        token = ''
        if request.headers.get('Authorization'):
            token = jwt.decode(request.headers.get('Authorization'),app.config['SECRET_KEY'])
        print(token,'token')
        cursor = mydb.cursor(pymysql.cursors.DictCursor)
        if token:
            bodyParams = request.get_json()
            print(bodyParams,'bodyParams')
            if request.method == 'POST':
                #cursor = mydb.cursor(pymysql.cursors.DictCursor)
                sqlQuery = "UPDATE users SET name=%s,username=%s,mobile=%s,email=%s,dob=%s,job=%s,education=%s,address=%s "
                values = (bodyParams['name'],bodyParams['username'],bodyParams['mobile'],bodyParams['email'],bodyParams['dob'],bodyParams['job'],bodyParams['education'],bodyParams['address'])
                cursor.execute(sqlQuery, values )
                mydb.commit()
                resp = jsonify({'result':{'message':'User added successfully','status':0}})
                resp.status_code = 200
                resp.headers={"content-type":"application/json"}
                return resp
            else:
                resp = jsonify({'result':{'message':'Something is not good','status':-1}})
                return resp
        else:
            resp = jsonify({'result':{'message':'User not authorized','status':-1}})
            return resp
    except Exception as e:
        print(e)
        resp = jsonify({'result':{'message':'Something is not good/Exception','status':-1}})
        return resp
    finally:
        cursor.close() 
        #mydb.close()
      

if __name__ == '__main__':
    SocketIo.run(app,port=5000)
#app.run()