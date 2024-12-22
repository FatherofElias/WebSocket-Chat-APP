from web_socket_server import WebSocketServer, socketio
from flask import render_template

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
        print(f'Received message from {author}: {message}')
        socketio.emit('message', {'author': author, 'message': message})

@socketio.on('get_user_messages')
def handle_get_user_messages(data):  
    all_messages = []
    for author, messages in message_storage.items():
        for message in messages:
            all_messages.append({'author': author, 'message': message})
    print(f'Sending all messages: {all_messages}')
    socketio.emit('get_user_messages', {'messages': all_messages})

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
