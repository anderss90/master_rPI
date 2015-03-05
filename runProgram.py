import backEnd.backEnd
import upstream
import downstream
from serverThread import flaskServerThread

flaskServerThread = flaskServerThread()
backendthread = backEnd.backEnd.backEndThread(1)

backendthread.start()
flaskServerThread.start()

