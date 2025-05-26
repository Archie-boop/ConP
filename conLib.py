##########################
### Библиотека ConP    ###
##########################
### Автор : Archie     ###
### Дата  : 08.03.2025 ###
### Версия: #0001      ### 
##########################

####################################################
#                                                  #
# Библиотека предназначена для работы с протоколом #
# DMconnect версии v3 #4                           #
#                                                  #
####################################################

####################################################
## Подключение дополнительных библиотек

import time
import socket
import threading

####################################################
## Команды

LOGIN_CMD = "/login" # /login xxx xxx
REG_CMD = "/register" # /register xxx xxx
PM_CMD = "/pm" # /pm xxx xxx
ACT_CMD = "/act" # /act xxx
SERVERS_CMD = "/list_servers" # /list_servers
JOIN_SRV_CMD = "/join_server" # /join_server xxx
CREATE_SRV_CMD = "/create_server" # /create_server xxx
USERS_CMD = "/members" # /members
HELP_CMD = "/help" # /help
KEEP_ALIVE = "/" # keep-alive сообщение

####################################################
## Разделители

CMD_SEP = " "  # разделитель команд
MSG_SEP = ": " # разделитель сообщений

####################################################
## Нужные нам ответы сервера

KEEP_ALIVE_ANS = "Unknown command." # ответ на keep-alive

####################################################
## Дополнительные параметры

BUFFER = 1024 # размер буфера при обмене сообщениями в байтах
SLEEP = 0.2   # время ожидания между отправкой сообщений
sock = None   # переменная клиентского сокета
sent_i = 1    # который раз мы отправляем сообщение
DEBUG = True  # включить ли отладку всего происходящего
KEEP_ALIVE_INTERVAL = 5  # интервал keep-alive в секундах
_keep_alive_thread = None
_keep_alive_stop_event = None

####################################################
## Функции для составления команд

def MAKE_PM(to, msg):
	return PM_CMD+CMD_SEP+to+CMD_SEP+msg

def MAKE_ACT(act):
	return ACT_CMD+CMD_SEP+act

def MAKE_JOIN_SERVER(server):
	return JOIN_SRV_CMD+CMD_SEP+server

def MAKE_CREATE_SERVER(server):
	return CREATE_SRV_CMD+CMD_SEP+server

def MAKE_LOGIN(username, password):
	return LOGIN_CMD+CMD_SEP+username+CMD_SEP+password

def MAKE_REGISTER(username, password):
	return REG_CMD+CMD_SEP+username+CMD_SEP+password

####################################################
## Функции для отправки команд

def pm(to, msg):
	send_msg(MAKE_PM(to, msg))

def act(act):
	send_msg(MAKE_ACT(act))

def join_server(server):
	send_msg(MAKE_JOIN_SERVER(server))

def create_server(server):
	send_msg(MAKE_CREATE_SERVER(server))

def login(username, password):
	send_msg(MAKE_LOGIN(username, password))

def register(username, password):
	send_msg(MAKE_REGISTER(username, password))

####################################################
## Функции для работы с сервером

def send_msg(msg):
	global sock
	global sent_i

	if DEBUG:
		print("<2><" + str(sent_i) + "> >>> TCP cmd send msg size: " + str(len(msg)))
		print("<2><" + str(sent_i) + ">     " + str(msg))

	if msg.strip():
		time.sleep(SLEEP)
		sent_i = sent_i + 1
		sock.send(msg.strip().encode('utf-8'))

		if DEBUG:
			print("<2><" + str(sent_i) + "> <<< " + str(decode_hex(msg.encode('utf-8'))) + "\n")
			
		return True
	else:
		return False

def decode_hex(msg):
	return ' '.join(f"{byte:02X}" for byte in msg)

def connect(server, port):
	global sock
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((server, port))

	if DEBUG:
		print(">>>> " + str(server) + ":" + str(port) + " <<<<")
	time.sleep(SLEEP*5)


	if DEBUG:
		print("<1><1> >>> TCP cmd connect on  " + str(port) + " : " + str(BUFFER) + " bytes")
	start_recv = sock.recv(BUFFER)


	if DEBUG:
		print("<1><2> called for utf-8 TCP_CMD")
	start_msg = start_recv.decode('utf-8')

	if DEBUG:
		print("<1><3> <<< " + str(decode_hex(start_recv)))

	return sock, start_msg

def _keep_alive_loop():
	global sock
	while not _keep_alive_stop_event.is_set():
		try:
			if sock:
				# Отправляем keep-alive команду
				if DEBUG:
					print("<4><1> >>> TCP cmd keep-alive")
					print("<4><2>     " + str(decode_hex(KEEP_ALIVE.encode('utf-8'))) + "\n")
					
				sock.send(KEEP_ALIVE.encode('utf-8'))
		except Exception as e:
			if DEBUG:
				print(str(e))
		_keep_alive_stop_event.wait(KEEP_ALIVE_INTERVAL)


def start_keep_alive():
    """Запустить keep-alive поток."""
    global _keep_alive_thread, _keep_alive_stop_event
    if _keep_alive_thread and _keep_alive_thread.is_alive():
        return  # Уже запущен
    _keep_alive_stop_event = threading.Event()
    _keep_alive_thread = threading.Thread(target=_keep_alive_loop, daemon=True)
    _keep_alive_thread.start()


def stop_keep_alive():
    """Остановить keep-alive поток."""
    global _keep_alive_thread, _keep_alive_stop_event
    if _keep_alive_stop_event:
        _keep_alive_stop_event.set()
    if _keep_alive_thread:
        _keep_alive_thread.join(timeout=1)
    _keep_alive_thread = None
    _keep_alive_stop_event = None

####################################################
## Функции для работы с полученными сообщениями

def split_msg(msg):
	if ": " in text:
		name, message = text.split(": ", 1)
		return name.strip(), message

	return None, text

def parse_list(prefix, msg):
    if msg.startswith(prefix):
        servers_str = msg[len(prefix):].strip()
        return [server.strip() for server in servers_str.split(',') if server.strip()]
    else:
        return []

def receive_messages(stop_event, do=None):
    global sock
    while not stop_event.is_set():
        try:
            message = sock.recv(BUFFER).decode('utf-8').strip()

            if not message:
                break

            message = message.replace(KEEP_ALIVE_ANS, "")

            if not messag.strip():
            	continue

            if DEBUG:
                print("<3><1> <<< TCP cmd recv msg size: " + str(len(message)))
                print("<3><2>     " + str(decode_hex(message.encode('utf-8'))))
                print("<3><3> <<< " + str(message) + "\n")

            if do:
                do(message)
        except Exception as e:
            if not stop_event.is_set():
                print("Ошибка при получении сообщения: " + str(e))
            break

                                                  ##
####################################################