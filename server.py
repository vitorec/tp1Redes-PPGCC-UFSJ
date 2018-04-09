import os
import sys
import socket
import argparse

BUFFER_SIZE = 2048


class Server:

	def __init__(self, host, port):
		self.host = host
		self.port = port
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			print('Falha ao criar o socket')
			sys.exit()
		print('Socket criado\n')

	def initialize(self):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind((self.host, self.port))
		self.socket.listen(1)
		os.chdir('public')
		print('Server pronto\n')

	def run(self):
		client_socket, address = self.socket.accept()
		request = client_socket.recv(BUFFER_SIZE).decode('utf-8')
		response = Server.handle_request(request)
		try:
			client_socket.send(response)
			client_socket.close()
		except Exception as e:
			print(e)

	@staticmethod
	def handle_request(request):
		response = ''
		request_error = False
		path = ''
		try:
			method = request.split(' ')[0]
			path = request.split(' ')[1]
			protocol = request.split(' ')[2]

			if method != 'GET':
				response = Server.error_message(400, '400 bad request')
				request_error = True

		except:
			response = Server.error_message(400, '400 bad request')
			request_error = True

		if not request_error:

			if path == '/':
				if os.path.isfile('index.html'):
					response = Server.read_file('index.html')
				else:
					response = Server.list_files()
					print(response)
			else:
				files = os.listdir()
				file = path[1:]
				if file in files:
					response = Server.read_file(file)
				else:
					response = Server.error_message(404, '404 file not found')

		return response

	@staticmethod
	def read_file(file):
		ext = file.split('.')[1]
		content_type = 'text/html'
		if ext == 'jpg' or ext == 'jpeg':
			content_type = 'image/jpeg'

		return 'HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n'.format(content_type).encode('utf-8') + open(file, 'rb').read()

	@staticmethod
	def list_files():
		files = os.listdir()
		print(files)
		list = ''
		for file in files:
			list += "<li><a href=/{0}>{0}</a></li>".format(file)

		response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n' \
				   '<!DOCTYPE html><html lang="pt-br"><meta charset="UTF-8"><body><ul>{0}</ul></body></html>'.format(list).encode('utf-8')
		return response

	@staticmethod
	def error_message(code, message):
		return """
			HTTP/1.1 {} ERROR
			Content-Type: text/html
			
			<!DOCTYPE html>
			<html lang='pt-br'>
			<meta charset="UTF-8">
			<body>
			<h1>{}</h1>
			</body>
			</html>
		""".format(code, message).encode('utf8')



def main():
	parser = argparse.ArgumentParser(description='Server TCP')
	parser.add_argument('-s', '--host', type=str, default='localhost', help='Host (host padrão: "localhost"')
	parser.add_argument('-p', '--port', type=int, default=12000, help='Porta (porta padrão: 12000)')

	args = parser.parse_args()
	host = args.host
	port = args.port

	server = Server(host, port)
	server.initialize()

	while True:
		server.run()


if __name__ == '__main__':
	main()
