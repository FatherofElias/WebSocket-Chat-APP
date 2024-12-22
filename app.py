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
    print(f"Received data for get_user_messages: {data}")
    if isinstance(data, dict):
        author = data.get('author')  
        if author in message_storage:
            user_messages = [{'author': author, 'message': msg} for msg in message_storage[author]]
        else:
            user_messages = []

        print(f"Sending messages for {author}: {user_messages}")
        socketio.emit('get_user_messages', {'messages': user_messages})
    else:
        print("Data received in unexpected format")

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
