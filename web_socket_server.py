from flask import Flask
from flask_socketio import SocketIO, join_room

socketio = SocketIO()

class WebSocketServer:
    def __init__(self, debug=False):
        self.app = self.create_app(debug)

    def create_app(self, debug=False):
        app = Flask(__name__)
        app.debug = debug
        socketio.init_app(app, cors_allowed_origins="*")
        return app
