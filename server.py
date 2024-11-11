from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}
calls = {}

@app.route("/")
def index():
    return "WebRTC Signaling Server Running"

@socketio.on("join")
def on_join(data):
    username = data["username"]
    users[username] = request.sid
    print(f"User {username} joined with SID {request.sid}")

@socketio.on("call")
def on_call(data):
    callee = data["to"]
    caller = data["from"]
    calls["caller"] = caller
    calls["callee"] = callee
    if callee in users:
        emit("call-received", {"from": caller, "to": callee}, room=users[callee])
    else:
        emit("user-unavailable", {"message": "User is not online"}, room=users[caller])

@socketio.on("accept-call")
def on_accept_call(data):
    caller = calls.get("caller")
    callee = calls.get("callee")
    if caller and caller in users:
        emit("call-accepted", {"message": "Call accepted", "to": callee, "from": caller}, room=users[caller])

@socketio.on("reject-call")
def on_reject_call(data):
    caller = calls.get("caller")
    if caller and caller in users:
        emit("call-rejected", {"message": "Call rejected"}, room=users[caller])

@socketio.on("offer")
def on_offer(data):
    callee = calls.get("callee")
    if callee and callee in users:
        emit("offer", data, room=users[callee])

@socketio.on("answer")
def on_answer(data):
    caller = calls.get("caller")
    if caller and caller in users:
        emit("answer", data, room=users[caller])

@socketio.on("ice-candidate")
def on_ice_candidate(data):
    receiver = calls.get("callee")
    if receiver in users:
        emit("ice-candidate", data, room=users[receiver])

@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    for username, user_sid in list(users.items()):
        if user_sid == sid:
            del users[username]
            print(f"User {username} disconnected")
            break

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
