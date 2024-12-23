from web_socket_server import WebSocketServer, socketio
from flask_socketio import join_room
from flask import render_template, request, redirect, url_for
import json

server = WebSocketServer(debug=True)
app = server.app
message_storage = {}

@app.route('/chat')
def index():
    return render_template('join_room.html')

@app.route('/')
def chat():
    room = request.args.get('room')
    author = request.args.get('author')
    if not room or not author:
        return redirect(url_for('index'))
    return render_template('WebSocketClient.html', room=room, author=author)

@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    author = data.get('author')
    if author and room:
        join_room(room)
        print(f'User {author} joined room {room}')
        socketio.emit('join', {'author': author, 'room': room}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data.get('room')
    author = data.get('author')
    message = data.get('message')
    if room and author and message:
        print(f'Message from {author} in {room}: {message}')
        if author not in message_storage:
            message_storage[author] = []
        message_storage[author].append(message)
        socketio.emit('message', {'author': author, 'message': message}, room=room)

@socketio.on('get_user_messages')
def handle_get_user_messages(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)

        author = data.get('author')
        room = data.get('room')
        if author in message_storage:
            user_messages = [{'author': author, 'message': msg} for msg in message_storage[author]]
        else:
            user_messages = []

        print(f'Retrieving messages for {author} in room {room}')
        socketio.emit('get_user_messages', {'author': author, 'messages': user_messages}, room=room)
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

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000)
