# Тест библиотеки ConP

import conLib
import threading

def reprint(string):
	print(":::" + str(string))

sock, _ = conLib.connect('localhost', 1111)
conLib.login('user', 'mysecretpassword')
conLib.start_keep_alive()
conLib.receive_messages(threading.Event(), reprint)