import os
import sys
import socket
import argparse
from io import StringIO

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
		"""Configura o socket"""
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind((self.host, self.port))
		self.socket.listen(1)
		os.chdir('public')
		print('Server pronto\n')

	def run(self):
		client_socket, address = self.socket.accept()
		request = client_socket.recv(BUFFER_SIZE).decode('utf-8')
		print(request)

		try:
			# extrai os cabeçalhos da requisição
			headers = Server.extract_headers(request)

			Server.print_headers(headers)
		except:
			pass

		# trata a requisição
		response = Server.handle_request(request)

		try:
			# envia a resposta
			client_socket.send(response)
			client_socket.close()
		except Exception as e:
			print(e)

	@staticmethod
	def extract_headers(request):
		headers = dict()
		first_line = request.split('\r\n\r\n')[0].split('\r\n', 1)[0]
		headers['Method'] = first_line.split(' ')[0]
		headers['Path'] = first_line.split(' ')[1]
		headers['Protocol'] = first_line.split(' ')[2]

		lines = request.split('\r\n\r\n')[0].split('\r\n', 1)[1]
		headers_data = StringIO(lines)

		for line in headers_data:
			line = line.replace('\r\n', '')
			key = line.split(': ', 1)[0]
			value = line.split(': ', 1)[1]
			headers[key] = value
		return headers

	@staticmethod
	def print_headers(headers):
		print('Cabeçalhos:')
		for key, value in headers.items():
			print('{0:<30}: {1:<50}'.format(key, value))
		print('')

	@staticmethod
	def handle_request(request):
		"""Trata a requisição"""
		response = ''
		request_error = False
		path = ''
		try:
			method = request.split(' ')[0]
			path = request.split(' ')[1]

			# se não for o método GET, envia erro 400
			if method != 'GET':
				response = Server.error_message(400, '400 bad request')
				request_error = True

		except:
			# se houver erro na requisição, envia erro 400
			response = Server.error_message(400, '400 bad request')
			request_error = True

		# se a requisição estiver correta
		if not request_error:

			if path == '/':
				# se encontrar o index.html na raiz
				if os.path.isfile('index.html'):
					response = Server.read_file('index.html')
				# se não, faz a listagem dos arquivos
				else:
					response = Server.list_files()
			else:
				files = os.listdir()
				file = path[1:]
				# envia o arquivo se for encontrado
				if file in files:
					response = Server.read_file(file)
				# 404 se não existir
				else:
					response = Server.error_message(404, '404 file not found')

		return response

	@staticmethod
	def read_file(file):
		"""Monta a resposta com os bytes do arquivo"""
		ext = file.split('.')[1]
		content_type = 'text/html'
		if ext == 'jpg' or ext == 'jpeg':
			content_type = 'image/jpeg'
		elif ext == 'ico':
			content_type = 'image/x-icon'
		print(file)
		return 'HTTP/1.1 200 OK\r\nContent-Type: {}\r\n\r\n'.format(content_type).encode('utf-8') + open(file, 'rb').read()

	@staticmethod
	def list_files():
		"""Monta a resposta com a listagem de arquivos na raiz"""
		files = os.listdir()
		list = ''
		for file in files:
			size = Server.get_file_size(file)
			list += "<tr><td><a href=/{0}>{0}</a></td><td>{1}</td></tr>".format(file, size)

		style = '''<style>
			table {
				font-family: arial, sans-serif;
				border-collapse: collapse;
				width: 100%;
			}
			td, th {
				border: 1px solid #dddddd;
				text-align: left;
				padding: 8px;
			}
			tr:nth-child(even) {
				background-color: #eee;
			}
			</style>'''
		response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' \
			'<!DOCTYPE html><html lang="pt-br"><head><meta charset="UTF-8">' \
			'<link rel="icon" type="image/x-icon" href="favicon.ico" />{0}</head>' \
			'<body><table style="width: 50%"><tr><th>Filename</th><th>Size</th></tr>' \
			'<tbody>{1}</tbody></table></body></html>'.format(style, list).encode('utf-8')
		return response

	@staticmethod
	def error_message(code, message):
		"""Resposta com mensagem de erro"""
		return 'HTTP/1.1 {} ERROR\nContent-Type: text/html\n\n' \
			'<!DOCTYPE html><html lang="pt-br"><meta charset="UTF-8">' \
			'<body><h1>{}</h1></body></html>'.format(code, message).encode('utf-8')

	@staticmethod
	def get_file_size(file):
		"""Obtem o tamanho do arquivo"""
		if os.path.isdir(file):
			return ''
		file_size = os.stat(file).st_size
		size = ''
		for count in ['Bytes', 'KB', 'MB', 'GB']:
			if -1024.0 <= file_size <= 1024.0:
				size = '{0:3.1f} {1}'.format(file_size, count)
				break
			file_size /= 1024.0
		return size


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
		print('Aguardando nova requisição')
		server.run()
		print('-----------------------')


if __name__ == '__main__':
	main()
