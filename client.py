import re
import argparse
from socket import *
from urllib.parse import urlparse


class Client:

	def __init__(self, url):
		parsed = Client.parse_url(url)
		self.protocol = parsed['protocol']
		self.hostname = parsed['hostname']
		self.path = parsed['path']
		self.port = parsed['port']
		self.socket = socket(AF_INET, SOCK_STREAM)

	def run(self):
		self.socket.connect((self.hostname, self.port))

		request = input('Input lowercase sentence: ')

		self.socket.send(bytes(request.encode('utf-8')))

		response = self.socket.recv(1024)
		print('From Server:\n')
		print(str(response, 'utf-8'))

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
		parsed_url['protocol'] = o.scheme if o.scheme else 'http'
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
