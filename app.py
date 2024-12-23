from web_socket_server import WebSocketServer, socketio
from flask import render_template
import json

server = WebSocketServer()
app = server.app
message_storage = {}

@socketio.on('message')
def handle_message(data):
    author = data.get('author')
    message = data.get('message')
    if author and message:
        if author not in message_storage:
            message_storage[author] = []
        message_storage[author].append(message)
        socketio.emit('message', {'author': author, 'message': message})

@socketio.on('get_user_messages')
def handle_get_user_messages(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)  

        author = data.get('author')
        if author in message_storage:
            user_messages = [{'author': author, 'message': msg} for msg in message_storage[author]]
        else:
            user_messages = []

        socketio.emit('get_user_messages', {'author': author, 'messages': user_messages})
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        socketio.emit('error', {'message': 'Invalid JSON format'})
    except Exception as e:
        print(f"Error: {e}")
        socketio.emit('error', {'message': 'An error occurred during message retrieval'})

@socketio.on('connect')
def handle_connect():
    print('Client Connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client Disconnected')

@app.route('/')
def index():
    return render_template('WebSocketClient.html')

if __name__ == '__main__':
    socketio.run(app)
