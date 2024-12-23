from web_socket_server import WebSocketServer, socketio
from flask_socketio import join_room, leave_room
from flask import render_template, request, redirect, url_for
import json

server = WebSocketServer(debug=True)
app = server.app
message_storage = {}
chat_rooms = {}  

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
        if room not in chat_rooms:
            chat_rooms[room] = []
        chat_rooms[room].append(author)
        socketio.emit('join', {'author': author, 'room': room}, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data.get('room')
    author = data.get('author')
    if author and room:
        leave_room(room)
        print(f'User {author} left room {room}')
        if room in chat_rooms:
            chat_rooms[room].remove(author)
            if not chat_rooms[room]:
                del chat_rooms[room]
        socketio.emit('leave', {'author': author, 'room': room}, room=room)

@socketio.on('message')
def handle_message(data):
    room = data.get('room')
    author = data.get('author')
    message = data.get('message')
    if room and author and message:
        print(f'Message from {author} in {room}: {message}')
        if author not in message_storage:
            message_storage[author] = []
        message_storage[author].append({'message': message, 'id': len(message_storage[author])})
        socketio.emit('message', {'author': author, 'message': message, 'id': message_storage[author][-1]['id']}, room=room)

@socketio.on('edit_message')
def handle_edit_message(data):
    room = data.get('room')
    author = data.get('author')
    message = data.get('message')
    message_id = data.get('id')
    if room and author and message and message_id is not None:
        print(f'Editing message from {author} in {room}: {message}')
        if author in message_storage and len(message_storage[author]) > message_id:
            message_storage[author][message_id]['message'] = message
            socketio.emit('edit_message', {'author': author, 'message': message, 'id': message_id}, room=room)

@socketio.on('delete_message')
def handle_delete_message(data):
    room = data.get('room')
    author = data.get('author')
    message_id = data.get('id')
    if room and author and message_id is not None:
        print(f'Deleting message from {author} in {room}')
        if author in message_storage and len(message_storage[author]) > message_id:
            message_storage[author] = [msg for msg in message_storage[author] if msg['id'] != message_id]
            socketio.emit('delete_message', {'author': author, 'id': message_id}, room=room)

@socketio.on('get_user_messages')
def handle_get_user_messages(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)  

        author = data.get('author')
        room = data.get('room')
        if author in message_storage:
            user_messages = [{'author': author, 'message': msg['message'], 'id': msg['id']} for msg in message_storage[author]]
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