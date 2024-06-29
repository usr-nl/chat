from flask import Flask,request
import pandas # may cause performance issues. 
import random

app=Flask(__name__)

messages=pandas.DataFrame(columns=["sender","receiver","content"])
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
    f=""
    user_now=request.args.get("IP")
    if user_now!=None and user_now!="":
        if user_now in users.index:
            (users.at[user_now,"status"])^=True
        else:
            f="not a valid user<br>"
    return f+users_box+get_users()

def get_messages():
    messagelist=""
    for id in messages.index:
        messagelist+=str(id)+" "+messages.at[id,"sender"]+" "+messages.at[id,"receiver"]+" "+messages.at[id,"content"]+" <br>"
    return messagelist

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
    token_now=request.args.get("Token")
    if token_now!=token:
        return token_box+"invalid input"
    f=""
    global messages
    message_now=request.args.get("ID")
    if message_now!=None and message_now!="":
        if message_now.isdigit() and (int(message_now) in messages.index):
            messages=messages.drop(int(message_now))
        else:
            f="not a valid message"
    return f+message_box+get_messages()

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
        if name in users.name.values or not (name.isalnum() and name.isascii()):
            f="invalid input<br>"
        else:
            ip=request.remote_addr
            if ip not in users.index:
                users.at[ip,"status"]=True
            users.at[ip,"name"]=name
    ip=request.args.get("IP")
    if ip==None or ip=="":
        ip=request.remote_addr
    profile_info=""
    profile_info+="IP: %s<br>"%(ip)
    if ip in users.index:
        profile_info+="Name: %s"%(users.at[ip,"name"])
    else:
        profile_info+="Choose a nichname"
    return name_box+f+profile_info

#main pages
def send(sender,receiver,content):
    global messages
    messages=pandas.concat([messages,pandas.DataFrame({"sender":[sender],"receiver":[receiver],"content":[content]},index=[None])],ignore_index=True)

send_box=\
'''
<form>
  Receiver: 
  <select name="Receiver" id="Receiver">
    <option value=>All</option>
    CHOOSE_RECEIVER
  </select><br>
  Message: 
  <input type="text" name="Message"><br>
  <input type="submit" value="Submit">
</form>
<a href="/profile">Profile</a>
<a href="/settings">Manage</a><br>
'''
def get_choose():
    choose_receiver=""
    for receiver in users[users.status==True].index:
        ip,name=receiver,users.at[receiver,"name"]
        choose_receiver+='    <option value="%s">%s</option>\n'%(ip,name)
    return send_box.replace("CHOOSE_RECEIVER",choose_receiver)

def get_page(ip):
    page=""
    messages_filtered=messages[(messages.receiver=='')|(messages.receiver==ip)|(messages.sender==ip)].sort_index()
    for message in messages_filtered.values:
        sender,receiver,content=message
        sender="<a href=/profile?IP=%s>%s</a>"%(sender,users.at[sender,"name"])
        if receiver!='':
            receiver="<a href=/profile?IP=%s>%s</a>"%(receiver,users.at[receiver,"name"])
        if receiver!='':
            page=sender+"(to %s)"%(receiver)+"<br>"+content+"<br>"+page
        else:
            page=sender+"<br>"+content+"<br>"+page
    return page

@app.route("/")
def chat():
    f=""
    ip=request.remote_addr
    if ip in users.index and users.at[ip,"status"]==False:
        return "banned"
    content=request.args.get("Message")
    if content=='':
        content=None
    receiver=request.args.get("Receiver")
    if receiver==None:
        receiver=''
    if content!=None:
        if ip in users.index:
            if "<" in content or ">" in content:
                f="invalid message<br>"
            elif receiver not in users.index and receiver!='':
                f="invalid receiver<br>"
            else:
                send(ip,receiver,content)
        else:
            f="Please set your username first<br>"
    send_box=get_choose()
    page=get_page(ip)
    return send_box+f+page

app.run(host="0.0.0.0",port=80)
