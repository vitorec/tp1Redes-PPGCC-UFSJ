import re
import sys
import time
import socket
import argparse
from urllib.parse import urlparse

BUFFER_SIZE = 2048


class Client:

	def __init__(self, url):
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

	def recv_response(self, timeout=1):
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

		request = self.make_request()

		try:
			self.socket.send(request)
		except socket.error:
			print('Falha ao enviar requisição')
			sys.exit()

		response = self.recv_response()

		print(response.decode('utf-8'))

		self.socket.close()

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
		return parsed_url

	def print(self):
		print('Client HTTP ', self)
		print('Protocol: ', self.protocol)
		print('Hostname: ', self.hostname)
		print('Path: ', self.path)
		print('Port: ', self.port)


def main():

	parser = argparse.ArgumentParser(description='Client HTTP')
	parser.add_argument('-u', '--url', type=str, default='http://localhost:12000',
						help='Server URL (default is "http://localhost:12000"')

	args = parser.parse_args()
	url = args.url
	client = Client(url)
	client.run()


if __name__ == "__main__":
	main()
