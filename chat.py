# This version may have lots of issues. 

from flask import Flask,request
import pandas # may cause performance issues. 
import random

def get_token():
    token=[]
    for i in range(25):
        now=random.randint(0,35)
        if now<10:
            token.append(chr(ord('0')+now))
        else:
            token.append(chr(ord('a')+now-10))
    token="".join(token)
    print(token)
    return token

token=get_token()

app=Flask(__name__)

users=pandas.DataFrame(columns=["name","status"])
starter_box=\
'''
<form>
  Choose a nichname: <input type="text" name="Name"><br>
  <input type="submit" value="Submit">
</form>
'''
def start(ip):
    global users
    name=request.args.get("Name")
    if name==None or name=='':
        return starter_box
    else:
        if name in users.name.values:
            return starter_box+"invalid input"
        users=pandas.concat([users,pandas.DataFrame({"name":[name],"status":[True]},index=[ip])])
        return "Reload the page to start chatting"

messages=pandas.DataFrame(columns=["sender","receiver","message"])
def send(sender,receiver,message):
    global messages
    messages=pandas.concat([messages,pandas.DataFrame({"sender":[sender],"receiver":[receiver],"message":[message]},index=[None])],ignore_index=True)

def get_choose():
    choose_receiver=""
    for receiver in users[users.status==True].index:
        ip,name=receiver,users.at[receiver,"name"]
        choose_receiver+='    <option value="%s">%s</option>\n'%(ip,name)
    return choose_receiver

def get_userlink(ip):
    return "<a href=/profile?IP=%s>%s</a>"%(ip,users.at[ip,"name"])

def get_page(sender):
    page=""
    msgs=messages[(messages.receiver=='')|(messages.receiver==sender)|(messages.sender==sender)].sort_index()
    for msg in msgs.values:
        sender_name,receiver_name,message=msg
        sender_name=get_userlink(sender_name)
        if receiver_name!='':
            receiver_name=get_userlink(receiver_name)
        if receiver_name!='':
            page=sender_name+"(to %s)"%(receiver_name)+"<br>"+message+"<br>"+page
        else:
            page=sender_name+"<br>"+message+"<br>"+page
    return page

@app.route("/")
def chat():
    sender=request.remote_addr
    if sender not in users.index:
        return start(sender)
    if users.at[sender,"status"]==False:
        return "banned"
    message=request.args.get("Message")
    if message=='':
        message=None
    receiver=request.args.get("Receiver")
    if receiver==None:
        receiver=''
    if message!=None:
        send(sender,receiver,message)
    choose_receiver=get_choose()
    page=get_page(sender)
    send_box=\
'''
<form>
  Receiver: 
  <select name="Receiver" id="Receiver">
    <option value=>All</option>
    %s
  </select><br>
  Message: 
  <input type="text" name="Message"><br>
  <input type="submit" value="Submit">
</form>
<a href="/profile">Profile</a>
<a href="/settings">Manage</a><br>
'''%(choose_receiver)
    return send_box+page

#profile pages afterwards
name_box=\
'''
<form>
  New Name: <input type="text" name="Name"><br>
  <input type="submit" value="Submit">
</form>
'''
@app.route("/profile")
def profile():
    f=""
    name=request.args.get("Name")
    if name!=None and name!="":
        if name in users.name.values:
            f="invalid input<br>"
        ip=request.remote_addr
        users.at[ip,"name"]=name
    ip=request.args.get("IP")
    if ip==None or ip=="":
        ip=request.remote_addr
    profile_info=\
'''
IP: %s<br>
Name: %s
'''%(ip,users.at[ip,"name"])
    return name_box+f+profile_info

#setting pages afterwards
token_box=\
'''
type 1 to regenerate token
<form>
  Token: <input type="text" name="Token"><br>
  <input type="submit" value="Submit">
</form>
'''

setting_links=\
'''
<a href="/settings/users">users</a><br>
<a href="/settings/messages">messages</a>
'''
@app.route("/settings")
def manage():
    global token
    token_now=request.args.get("Token")
    if token_now=="1":
        token=get_token()
    if token_now!=token:
        return token_box+"invalid input"
    return setting_links


users_box=\
'''
<form>
  Token: <input type="text" name="Token"><br>
  IP: <input type="text" name="IP"><br>
  <input type="submit" value="Submit">
</form>
'''
@app.route("/settings/users")
def manage_users():
    global token
    token_now=request.args.get("Token")
    if token_now=="1":
        token=get_token()
    if token_now!=token:
        return token_box+"invalid input"
    user_now=request.args.get("IP")
    if user_now!=None and user_now!="":
        (users.at[user_now,"status"])^=True
    return users_box+str(users).replace("\n","<br>\n")

message_box=\
'''
<form>
  Token: <input type="text" name="Token"><br>
  Message ID: <input type="text" name="ID"><br>
  <input type="submit" value="Submit">
</form>
'''
@app.route("/settings/messages")
def manage_messages():
    global token,messages
    token_now=request.args.get("Token")
    if token_now=="1":
        token=get_token()
    if token_now!=token:
        return token_box+"invalid input"
    message_now=request.args.get("ID")
    if message_now!=None and message_now!="":
        messages=messages.drop(int(message_now))
    return message_box+str(messages).replace("\n","<br>\n")

app.run(host="0.0.0.0",port=80)
