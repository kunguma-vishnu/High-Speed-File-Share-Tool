
import os
import sys
import socket
from PyQt5.QtWidgets import QMainWindow, QApplication,QPushButton,QLabel,QLineEdit,QFileDialog
from PyQt5.QtGui import QIcon

def isWIFIConnected():
    return (socket.gethostbyname(socket.gethostname()) != '127.0.0.1')

class Routes(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initializeHome()
        self.initUI()

    def initUI(self):
        self.move(300,100)
        self.setFixedSize(350,350)
        self.setWindowTitle('Share')
        self.setStyleSheet("QMainWindow{background-color : #FFFDE7;}QPushButton#receiveBtn{background-color : yellow; border : 1px solid #FFF; border-radius : 10px;}\
        QPushButton#sendBtn{background-color : #039BE5; border : 1px solid #FFF; border-radius : 12px;}QStatusBar{background-color : #0288D1}\
        QLabel#wifiConnection{font-size: 12px;padding: 0px 50px;}")
        self.setWindowIcon(QIcon('share-icon.png'))
        self.show()

    def initializeHome(self):
        self.statusBar().showMessage('Home')
        self.sendBtn = QPushButton('Send',self)
        self.sendBtn.move(120,150)
        self.sendBtn.setObjectName("sendBtn")
        self.receiveBtn = QPushButton('Receive',self)
        self.receiveBtn.move(120,200)
        self.receiveBtn.setObjectName("receiveBtn")

        self.wifiConnection = isWIFIConnected()
        self.wifiLabelText = ("No Network","Network Connected")[self.wifiConnection]
        self.wifiLabel = QLabel(self)
        self.wifiLabel.setText(self.wifiLabelText)
        self.wifiLabel.setGeometry(5,5,340,35)
        self.wifiLabel.setObjectName("wifiConnection")
        if(self.wifiConnection):
            self.wifiLabel.setStyleSheet("background-color : #5cb85c")
        else:
            self.wifiLabel.setStyleSheet("background-color : #d9534f")

        self.inputFriend = QLineEdit(self)
        self.inputFriend.move(1000,1000)
        self.inputFriend.setStyleSheet("background-color : white;border : 1px solid #888;border-radius: 12px;padding: 0px 70px;")

        self.connectBtn = QPushButton('Connect',self)
        self.connectBtn.move(1000,1000)
        self.connectBtn.setObjectName("connectFrnd")
        self.connectBtn.setStyleSheet("background-color : grey;border : 1px solid grey; border-radius : 12px;")

        self.fileChooser = QFileDialog(self)
        self.fileChooser.setFileMode(QFileDialog.AnyFile)

        self.chooseBtn = QPushButton('Choose File',self)
        self.chooseBtn.move(1000,1000)
        self.chooseBtn.setObjectName("Choose")
        self.chooseBtn.setStyleSheet("background-color : yellow;border : 1px solid white;border-radius : 12px;")

        self.sendBtn.clicked.connect(self.modeSelect)
        self.receiveBtn.clicked.connect(self.modeSelect)


    def modeSelect(self):
        mode = self.sender()
        self.statusBar().showMessage(mode.text())
        self.sendBtn.move(1000,1000)
        self.receiveBtn.move(1000,1000)
        print(mode.text())
        if(mode.text() == "Send"):
            self.inputFriend.setGeometry(50,150,250,30)
            self.connectBtn.move(120,200)
            self.connectBtn.clicked.connect(self.connectFrnd)
        elif(mode.text() == "Receive"):
            print("Receive mode")
            self.startServer()

    def startClient(self,destination):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((destination,3000))
        connectedSock = sock.recv(1024).decode()
        if connectedSock:
            self.statusBar().showMessage(connectedSock+" connected")
            self.connectBtn.move(1000,1000)
            self.inputFriend.move(1000,1000)
            self.chooseBtn.move(120,150)
            self.chooseBtn.clicked.connect(lambda: self.chooseFile(sock))


    def chooseFile(self,sock):
        if self.fileChooser.exec_():
            sock.send(str(os.path.getsize(self.fileChooser.selectedFiles()[0])).encode())
            sock.recv(1).decode()
            sock.send(str(os.path.basename(self.fileChooser.selectedFiles()[0])).encode())
            sock.recv(1).decode()
            with open(self.fileChooser.selectedFiles()[0],"rb") as f:
                data = f.read()
            sock.send(data)
            sock.recv(1).decode()
            sock.close()

    def connectFrnd(self):
        self.startClient(self.inputFriend.text())

    def startServer(self):
        self.serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.serverSocket.bind((socket.gethostname(),3000))
        print("Server binded")
        self.serverSocket.listen(1)
        self.start()

    def start(self):
        while True:
            try:
                self.clientSocket,self.clientAddress = self.serverSocket.accept()
                if self.clientSocket:
                    print(self.clientAddress)
                    self.statusBar().showMessage(socket.gethostbyaddr(self.clientAddress[0])[0])
                    self.clientSocket.send(socket.gethostname().encode())
                    fileSize = self.clientSocket.recv(1000).decode()
                    self.clientSocket.send("\n".encode())
                    print(fileSize+"\n")
                    fileName = self.clientSocket.recv(1000).decode()
                    self.clientSocket.send("\n".encode())
                    print(fileName+"\n")
                    data = self.clientSocket.recv(int(fileSize))
                    self.clientSocket.send("\n".encode())
                    with open(fileName,"wb") as file:
                        file.write(data);

            except socket.error as msg:            
                break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    route = Routes()
    sys.exit(app.exec_())
