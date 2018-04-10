import re
import os
import ssl
import sys
import time
import socket
import argparse
from urllib.parse import urlparse
from response import Response

BUFFER_SIZE = 2048


class Client:

	def __init__(self, url):
		# faz o parse na url
		parsed = Client.parse_url(url)
		self.protocol = parsed['protocol']
		self.hostname = parsed['hostname']
		self.path = parsed['path']
		self.port = parsed['port']
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			print('Falha ao criar o socket')
			sys.exit()
		print('Socket criado\n')

	def make_request(self):
		request = 'GET {} {}/1.1\r\nHost:{}\r\nConnection: close\r\n\r\n'.format(self.path, self.protocol, self.hostname)
		return bytes(request.encode('utf-8'))

	def recv_response(self, timeout=2):
		# non-blocking socket
		self.socket.setblocking(False)

		response = []
		data = ''

		start = time.time()
		while True:
			# se tiver algum dado, interrompe apos o timeout
			if response and time.time() - start > timeout:
				break

			# se não tiver nenhum dado, espera um pouco mais
			elif time.time() - start > timeout * 2:
				break

			try:
				data = self.socket.recv(BUFFER_SIZE)
				if data:
					response.append(data)
					# reinicia a contagem de tempo
					start = time.time()
			except:
				pass

		# junta as partes da resposta
		return b''.join(response)

	def run(self):
		self.socket.connect((self.hostname, self.port))
		if self.port == 443:
			self.socket = ssl.wrap_socket(self.socket, keyfile=None, certfile=None,
					server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)

		# cria a string de requisição
		request = self.make_request()

		print('\n------------------ REQUEST ------------------\n')
		print(request.decode())
		print('\n----------------------------------------------')

		try:
			self.socket.send(request)
		except socket.error:
			print('Falha ao enviar requisição')
			sys.exit()

		# obtem a resposta do servidor
		response_raw = self.recv_response()
		response = Response(response_raw)

		# log
		response.print()

		# se for código 200, escreve o arquivo
		if response.status['code'] == 200:
			self.write_file(response)
			print('Conexão fechada na porta ', self.port)

		# se houver redirecionamento retorna o código e a url
		elif str(response.status['code']).startswith('3'):
			return response.status['code'], response.headers['Location']

		# se houver erro, baixa o html
		elif str(response.status['code']).startswith('4'):
			self.write_file(response)

		self.socket.close()
		return response.status['code']

	def write_file(self, response):
		content_type = response.headers['Content-Type']
		path = 'temp/' + self.hostname

		ext = ''
		if content_type == 'text/plain':
			ext = '.txt'
		elif content_type == 'image/jpeg':
			ext = '.jpg'
		elif content_type == 'application/json':
			ext = '.json'
		else:
			ext = '.html'

		# cria os diretórios para guardar os arquivos
		os.makedirs(path, exist_ok=True)
		os.chdir(path)

		filename = self.path.rsplit('/', 1)[1]
		if filename == '':
			filename = 'index'
		if response.status['code'] != 200:
			filename = str(response.status['code'])
		if not filename.endswith(ext):
			filename += ext

		# escreve o arquivo
		file = open(filename, "wb")
		file.write(response.data)
		file.close()

	@staticmethod
	def parse_url(url):
		if '://' not in url:
			url = 'http://' + url
		port = None
		if re.findall('\:\d+', url):
			port = int(re.findall('\:\d+', url)[0].split(':')[1])
			url = url.replace(':' + str(port), '')
		o = urlparse(url)
		parsed_url = dict()
		parsed_url['protocol'] = o.scheme.upper() if o.scheme else 'HTTP'
		parsed_url['hostname'] = o.netloc
		parsed_url['path'] = o.path if o.path else '/'
		parsed_url['port'] = port if port else 80
		if url.startswith('https://'):
			parsed_url['port'] = 443
		return parsed_url

	def print(self):
		print('Client HTTP ', self)
		print('Protocol: ', self.protocol)
		print('Hostname: ', self.hostname)
		print('Path: ', self.path)
		print('Port: ', self.port)
		print('===========================')

def main():

	parser = argparse.ArgumentParser(description='Client TCP')
	parser.add_argument('-u', '--url', type=str, default='http://localhost:12000',
						help='Server URL (default is "http://localhost:12000"')

	args = parser.parse_args()
	url = args.url
	client = Client(url)
	client.print()
	code, location = client.run()
	if str(code).startswith('3'):
		print('\n################## REDIRECIONAMENTO ##################\n')
		client = Client(location)
		client.print()
		client.run()


if __name__ == "__main__":
	main()
