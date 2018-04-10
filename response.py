from io import StringIO


class Response:

	def __init__(self, response):
		self.status = Response.get_status(response)
		self.headers = Response.extract_headers(response)
		self.data = Response.extract_data(response)

	@staticmethod
	def get_status(response):
		"""Obtem o status code da resposta"""
		state_line = response.split(b'\r\n')[0].decode('utf-8')
		code = state_line.split(' ')[1]
		message = state_line.split(' ')[2]
		return {'code': int(code), 'message': message}

	@staticmethod
	def extract_headers(response):
		"""Extrai os cabeçalhos da resposta"""
		headers = dict()
		if b'\r\n' in response[:40]:
			lines = response.split(b'\r\n\r\n')[0].decode('utf-8').split('\r\n', 1)[1]
		elif b'\n' in response[:40]:
			lines = response.split(b'\n\n')[0].decode('utf-8').split('\n', 1)[1]
		headers_data = StringIO(lines)

		for line in headers_data:
			line = line.replace('\r\n', '')
			key = line.split(': ', 1)[0]
			value = line.split(': ', 1)[1]
			headers[key] = value
		return headers

	@staticmethod
	def extract_data(response):
		"""Extrai os dados da resposta"""
		if b'\r\n' in response[:40]:
			data = response.split(b'\r\n\r\n', 1)[1]
		elif b'\n' in response[:40]:
			data = response.split(b'\n\n', 1)[1]
		return data

	def print(self):
		print('\n------------------ STATUS ------------------\n')
		print(self.status)
		print('\n----------------- CABEÇALHOS ----------------\n')
		for key, value in self.headers.items():
			print('{0:<40}: {1:<50}'.format(key, value))
		print('\n-------------------- DATA -------------------\n')
		print(self.data[0:255])
		print('\n---------------------------------------------')

