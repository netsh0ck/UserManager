import werkzeug 
from werkzeug import * 
from werkzeug.utils import secure_filename 
werkzeug.cached_property = werkzeug.utils.cached_property
from flask import Flask, flash,request,session,render_template,redirect,url_for
from flask_restplus import Resource, Api
from flask_restplus import reqparse
import os
import json,psycopg2
import hashlib
import decimal
import random
import glob
import requests
app = Flask(__name__)
app.secret_key = os.urandom(24)
api = Api(app)
# Add the token that we copied
token="193546"
# Add your db details
conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')

@app.route('/home',methods=["GET","POST"])
def index():
    rr=''.join(random.choice('$idididiabcdEFGHijk?=lMNOpq1234567890rst') for _ in range(100))
    
    return render_template('login.html',rr=rr)

@app.route('/adminsec/news',methods=["GET","POST","PUT","DELETE"])
def adminsp():
    
    
    cursor=conn.cursor()
    try:
        cursor.execute("select news_link,news_tag from news;");
        res=cursor.fetchall()
        link=[]
        tag=[]
        for r in res:
            
            link.append(str(r[0]))
            tag.append(str(r[1]))
        
        return render_template('admin.html',ll=len(link),link=link,tag=tag)
    except Exception as e:
        return redirect(url_for('admin'))
    return redirect(url_for('adminsd'))
@app.route('/newuser',methods=["GET","POST"])
def newuser():
    return render_template('register.html')
@app.route('/logout',methods=["GET","POST"])
def logout():
    session['userid']=None
    session['username']=None
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile/<rr>',methods=["GET","POST"])
def profile(rr=None):
    
    if 'userid' not in session.keys():
        return redirect(url_for('index'))
    cursor=conn.cursor()
    try:
        cursor.execute("select news_link,news_tag from news;");
        res=cursor.fetchall()
        link=[]
        tag=[]
        for r in res:
            
            link.append(str(r[0]))
            tag.append(str(r[1]))
    except Exception as e:
        return redirect(url_for('profile'))
    return render_template('profilepage.html',ll=len(link),link=link,tag=tag,username=session['username'])


@api.route('/register',endpoint='register')
class UserRegistration(Resource):
    postparser = reqparse.RequestParser()
    postparser.add_argument('username',required=True, type=str,location='headers')
    postparser.add_argument('password',required=True, type=str,location='headers')
    

    @api.expect(postparser)
    def post(self):
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        username=request.headers.get('username')
        password=request.headers.get('password')
        
        
        ciphered_text = hashlib.md5(password.encode())
        cursor=conn.cursor()
        try:
            print("inside",flush=True)
            cursor.execute("Insert into user_management(username,password) values(%s,%s)",(username,ciphered_text.hexdigest()))
            conn.commit()
            
            return "User successfully registered",200
        except Exception as e:
            return "Something went wrong"+str(e),400
@api.route('/login',methods=["GET","POST"])
class login(Resource):
    postparser = reqparse.RequestParser()
    postparser.add_argument('username',required=True, type=str,location='headers')
    postparser.add_argument('password',required=True, type=str,location='headers')
    

    @api.expect(postparser)
    def post(self):
        session.pop('userid',None)
        username=request.headers.get('username')
        password=request.headers.get('password')
        print("trying for "+str(username),flush=True)
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')

        ciphered_text = hashlib.md5(password.encode())
        cursor=conn.cursor()
        try:
            cursor.execute("select * from user_management where username=%s and password=%s;",(username,ciphered_text.hexdigest()))
            res=cursor.fetchall()
            
            print(res,flush=True)
            if len(res)!=0:
                
                session['username']=json.dumps(res[0][0])
                session['userid']=res[0][-1]
                
                print(session['username'],flush=True)
                result= "Logged in successfully for user "+str(res[0][0]+str(session['userid']))
            else:
                result="User name or password is wrong"
                
                return {"data":str(result)},400
            
            print(result,flush=True)
            print(ciphered_text.hexdigest(),flush=True)
            return "user successfully logged in",200
        except Exception as e:
            return "Something went wrong"+str(e),400
     
@api.route('/adminsecretpageasalways',endpoint='adminsecretpageasalways')
class adminsecret(Resource):
    postparser = reqparse.RequestParser()
    postparser.add_argument('link',required=True, type=str,location='headers')
    postparser.add_argument('tag',required=True, type=str,location='headers')
    

    @api.expect(postparser)
    def post(self):
        #conn=psycopg2.connect(host='localhost',user='postgres',dbname='postgres',password='1234')
        link=request.headers.get('link')
        tag=request.headers.get('tag')
        print(link,flush=True)
        s=tag+"\n\n"+link
        
        cursor=conn.cursor()
        try:
            print("inside",flush=True)
            cursor.execute("Insert into news(news_link,news_tag) values(%s,%s)",(link,tag))
            conn.commit()
            jj="https://api.telegram.org/bot"+token+"/getUpdates"
            jj=requests.get(jj)
            
            jj=jj.json()
            chatid=str(jj['result'][-1]['message']['chat']['id'])
            baseurl="https://api.telegram.org/bot"+token+"/sendMessage?chat_id="+chatid+"&"
            baseurl+="text="+s
            print(baseurl,flush=True)
            requests.get(baseurl)
            return "User successfully registered",200
        except Exception as e:
            return "Something went wrong"+str(e),400
        
    


if __name__ == '__main__':
    app.run(debug=True)
    
