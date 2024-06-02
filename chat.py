from flask import Flask,request
import pandas # may cause performance issues. 
import random

app=Flask(__name__)

messages=pandas.DataFrame(columns=["sender","receiver","message"])
users=pandas.DataFrame(columns=["name","status"])

#setting pages afterwards
token=""

def get_token():
    global token
    token_list=[]
    for i in range(25):
        now=random.randint(0,35)
        if now<10:
            token_list.append(chr(ord('0')+now))
        else:
            token_list.append(chr(ord('a')+now-10))
    token="".join(token_list)
    print(token)
    token_save=open("token.key","w")
    token_save.write(token)
    token_save.close()

get_token()

token_box=\
'''
<form>
  Token: <input type="text" name="Token"><br>
  <input type="submit" value="Submit">
</form>
'''

setting_links=\
'''
<a href="/settings/users">users</a><br>
<a href="/settings/messages">messages</a><br>
<a href="/settings/reset">reset token</a>
'''
@app.route("/settings")
def manage():
    return setting_links

@app.route("/settings/reset")
def reset_token():
    token_now=request.args.get("Token")
    if token_now!=token:
        return token_box+"invalid input"
    get_token()
    return "token resetted"

def get_users():
    userlist=""
    for ip in users.index:
        userlist+=ip+" "+users.at[ip,"name"]+" "+str(users.at[ip,"status"])+" <br>"
    return userlist

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
    token_now=request.args.get("Token")
    if token_now!=token:
        return token_box+"invalid input"
    user_now=request.args.get("IP")
    if user_now!=None and user_now!="":
        (users.at[user_now,"status"])^=True
    return users_box+get_users()

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
    global messages
    token_now=request.args.get("Token")
    if token_now!=token:
        return token_box+"invalid input"
    message=request.args.get("ID")
    if message!=None and message!="":
        messages=messages.drop(int(message))
    return message_box+str(messages).replace("\n","<br>\n")

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

#main pages
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

def send(sender,receiver,content):
    global messages
    messages=pandas.concat([messages,pandas.DataFrame({"sender":[sender],"receiver":[receiver],"message":[content]},index=[None])],ignore_index=True)

def get_choose():
    choose_receiver=""
    for receiver in users[users.status==True].index:
        ip,name=receiver,users.at[receiver,"name"]
        choose_receiver+='    <option value="%s">%s</option>\n'%(ip,name)
    return choose_receiver

def get_userlink(ip):
    return "<a href=/profile?IP=%s>%s</a>"%(ip,users.at[ip,"name"])

def get_page(ip):
    page=""
    messages_filtered=messages[(messages.receiver=='')|(messages.receiver==ip)|(messages.sender==ip)].sort_index()
    for message in messages_filtered.values:
        sender,receiver,content=message
        sender=get_userlink(sender)
        if receiver!='':
            receiver=get_userlink(receiver)
        if receiver!='':
            page=sender+"(to %s)"%(receiver)+"<br>"+content+"<br>"+page
        else:
            page=sender+"<br>"+content+"<br>"+page
    return page

@app.route("/")
def chat():
    sender=request.remote_addr
    if sender not in users.index:
        return start(sender)
    if users.at[sender,"status"]==False:
        return "banned"
    content=request.args.get("Message")
    if content=='':
        content=None
    receiver=request.args.get("Receiver")
    if receiver==None:
        receiver=''
    if content!=None:
        send(sender,receiver,content)
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

app.run(host="0.0.0.0",port=80)
