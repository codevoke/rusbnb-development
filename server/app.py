from flask import Flask, render_template, send_file
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

CORS(app)


@app.route('/')
def index():
    return send_file('../index.html')  # Отдаем статический HTML-файл


@socketio.on('message')
def handle_message(message):
    # Обработка полученных сообщений
    print('Received message:', message)

    # Отправка ответного сообщения
    response = message
    emit('new_msg', response, room='chat_room', include_self=True)
 

@socketio.on('chat')
def join():
    print('\n\nJOIN USER')
    join_room('chat_room')


@socketio.on('connect')
def handle_connect():
    emit('connected')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)
# serve(app, host="0.0.0.0", port=80)
# serve - функция для запуска продакшен сервера. порт 80 - стандартный хттп порт,
# (можно будет заходить на http://localhost без указания порта)
