from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

CORS(app)

@socketio.on('connect')
@cross_origin()
def handle_connect():
    emit('connected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)