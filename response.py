from io import StringIO


class Response:

	def __init__(self, response):
		self.status = Response.get_status(response)
		self.headers = Response.extract_headers(response)
		self.data = Response.extract_data(response)

	@staticmethod
	def get_status(response):
		state_line = response.split(b'\r\n')[0].decode('utf-8')
		code = state_line.split(' ')[1]
		message = state_line.split(' ')[2]
		return {'code': int(code), 'message': message}

	@staticmethod
	def extract_headers(response):
		headers = dict()
		lines = response.split(b'\r\n\r\n')[0].decode('utf-8').split('\r\n', 1)[1]
		headers_data = StringIO(lines)

		for line in headers_data:
			line = line.replace('\r\n', '')
			key = line.split(': ', 1)[0]
			value = line.split(': ', 1)[1]
			headers[key] = value
		return headers

	@staticmethod
	def extract_data(response):
		data = response.split(b'\r\n\r\n')[1]
		return data

