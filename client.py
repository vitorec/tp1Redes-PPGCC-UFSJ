from socket import *

serverName = 'localhost'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

sentence = input('Input lowercase sentence: ')
clientSocket.send(sentence.encode('utf-8'))

response = clientSocket.recv(1024)
print('From Server: ', response.decode('utf-8'))

clientSocket.close()
