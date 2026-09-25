import json
import re
import pprint
import os
import sys
import time
import math
import socket

version_number = '0.1'
version_string = 'mtlf v' + version_number

class Config:
	r = re.compile("^([^=]*)=['\"](.*)['\"]$")
	def __init__(self, filename='/usr/local/etc/mtlf.conf'):
		self.filename = filename
		self.options = {}
		f = open(self.filename, 'r')
		while True:
			line = f.readline()
			if line:
				m = self.r.match(line)
				if(m):
					self.options[m.group(1)] = m.group(2)
			else:
				break

class Cards_dict:
	pp = pprint.PrettyPrinter(indent=4, width=40)
	# find data.json to load it
	def data_finder(self):
		home = os.environ.get('HOME')
		user_path = home + '/.mtlf/data.json'
		if os.path.exists(user_path):
			time_since_modified = math.floor(time.time() - os.path.getmtime(user_path)/(60*60*24))
			if time_since_modified > 30 and self.interactive:
				print('data.json hasn\'t been updated in ' + time_since_modified + ' days!')
				if input('update data now? [Y/n]').lower() == 'y':
					self.update_data()
			return user_path
	# unimplemented
	def update_data(self):
		return False
	# simple debug function that goes through each card
	# and tries the print_card() function, outputting the
	# name and layout of the card if it fails
	def test_print(self, verbose=False):
		for card in self.cards:
			try:
				if(verbose):
					print("Trying " + card['name'] + "...")
				print_card(card)
			except:
				print("couldn't print card " + card['name'] + " layout " + card['layout'])
		print("Done printing.")
	# filename:	 where to load data.json from
	# interactive:  this should be set to false if your utility is intended to be
	#			   piped or anything
	#
	# the cards in data.json are parsed from json objects
	# into python dicts, and appended to the self.cards array
	def __init__(self, filename=None, interactive=False):
		self.interactive = interactive
		if filename == None:
			filename = self.data_finder()
		self.file = open(filename, 'r')
		self.cards = []
		while True:
			line = self.file.readline()
			if(line):
				self.cards.append(json.loads(line))
			else:
				break
	# does the same thing as search_json, but instead of taking
	# key-value pairs, it takes a single string, in the form of
	# "key1=val1 key2=val2 key3=val3 [...]"
	def search_jsons(self, query_string, sort=None, cardattr=None):
		#args = []
		#r = re.compile('([^ =]*)="([^"]*)"|([^ =]*)=([^ ]*)')
		#for m in re.finditer(r, query_string):
		#	args.append(m.group(1) + '=' + m.group(2))
		args = query_string.split(' ')
		return self.search_json(args, sort, cardattr)
	# queries is a dict of key-value pairs
	# the keys correspond to the names of the fields in a card's
	# json object, and the values correspond to the values of those
	# fields. a card matches only if it matches every key-value pair.
	#
	# returns an array of all matches as card objects
	def search_json(self, queries, sort=None, cardattr=None):
		matches = []
		for card in self.cards:
			for face in get_faces(card):
				match = True
				for query in pattern_map(queries):
					if query[0] in face.keys():
						result = str(face[query[0]])
						if not re.search(query[1].lower(), result.lower().replace('\n', '').replace('\r', '')):
							match = False
				if match:
					matches.append(card)
			match = True
			for query in pattern_map(queries):
				if query[0] in card.keys():
					result = str(card[query[0]])
					if not re.search(query[1].lower(), result.lower().replace('\n', '').replace('\r', '')):
						match = False
			if match:
					matches.append(card)
					#break
		if sort == None:
			sorted_matches = sorted(matches, key=lambda x: x['name'])
			return sorted_matches
		else:
			unsorted = []
			for i in range(len(matches) - 1, 0, -1):
				if not sort[0] in matches[i].keys():
					unsorted.append(matches.pop(i))
			sorted_matches = sorted(matches, key=lambda x: x[sort[0]], reverse=sort[1])
			return sorted_matches + unsorted

class Client_dict(Cards_dict):
	def __init__(self, address, sock_type='AF_UNIX'):
		self.address = address
		self.sock_type = sock_type
	def search_json(self, queries):
		query_string = ' '.join(queries)
		return self.search_jsons(query_string)
	def search_jsons(self, query_string):
		if self.sock_type == 'AF_UNIX':
			self.sock = socket.socket(socket.AF_UNIX)
		elif self.sock_type == 'AF_INET':
			self.sock = socket.socket(socket.AF_INET)

		self.sock.connect(self.address)
		self.sock.send(bytes(query_string, 'utf-8'))

		return_bytes = b''
		return_buf = b''
		while True:
			return_buf = self.sock.recv(1024)
			return_bytes = return_bytes + return_buf
			if return_buf == b'':
				break

		return_str = bytes.decode(return_bytes, 'utf-8')
		return_json = json.loads(return_str)
		
		self.sock.close()
		return return_json

def make_dict(*args, **kwargs):
	config = Config()
	if 'sock_type' in config.options:
		sock_type = config.options['sock_type']
		if config.options['sock_type'] == 'AF_INET':
			address = (config.options['address'], int(config.options['port']))
		elif config.options['sock_type'] == 'AF_UNIX':
			address = config.options['address']
		c = Client_dict(address, sock_type)
	else:
		c = Cards_dict(*args, **kwargs)
	return c

class Server_dict(Cards_dict):
	def __init__(self, address, sock_type='AF_UNIX', *args, **kwargs):
		self.address = address
		if sock_type == 'AF_UNIX':
			self.sock = socket.socket(socket.AF_UNIX)
		elif sock_type == 'AF_INET':
			self.sock = socket.socket(socket.AF_INET)

		super().__init__(*args, **kwargs)

		self.sock.bind(self.address)
		self.sock.listen()

	def server_loop(self):
		while True:
			conn, address = self.sock.accept()
			self.handle_conn(conn)

	def handle_conn(self, conn):
		req_bytes = b''
		req_buf = b''
		while True:
			req_buf = conn.recv(1024)
			req_bytes = req_bytes + req_buf
			if len(req_buf) < 1024:
				break

		req_str = bytes.decode(req_bytes, 'utf-8')[:-1]
		print('request: \'' + req_str + '\'\n')
		resp_json = self.search_jsons(req_str)
		resp_str = json.dumps(resp_json)
		print('response: ' + str(resp_json) + '\n')
		resp_bytes = bytes(resp_str, 'utf-8')

		conn.sendall(resp_bytes)
		conn.close()

def sortby(item, sort):
	if sort in item.keys():
		return item[sort]
	else:
		return False

# this probably shouldn't exist
def pattern_map(query_arr):
	return_arr = []
	if len(query_arr) == 1 and not re.search('=', query_arr[0]):
		return_arr.append(('name', query_arr[0]))
	else:
		for item in query_arr:
			
			pair = re.split('=', item)
			if len(pair) == 2:
				#key = pair[0]
				#val = re.compile('"?([^"]*)"?').search(pair[1]).group(1)
				#return_arr.append((key, val))
                return_arr.append(pair[0], pair[1])
	return return_arr

# scryfall represents double-faced cards and other cards with alternative
# characteristics by having a 'card_faces' field containing an array of
# objects that then have the relevant data
#
# for example, if you wanted to search through cards' oracle text and
# wanted to make sure you hit the back of transforming carts, MDFCs etc,
# you can call get_faces() on a card to get an array of faces to iterate
# over, then perform your search on each face. on a double-faced card,
# this function will return an array of two elements, one for each face.
# called on a single-faced card, this will return a singleton array, which
# hopefully makes your function safe to call on both single-faced and
# double-faced cards.
def get_faces(card_dict):
	if 'card_faces' in card_dict.keys():
		return card_dict['card_faces']
	else:
		return [card_dict]

def format_card(card_dict, format_str=None):
	return_str = ''
	faces = get_faces(card_dict)
	if format_str == None:
		for face in faces:
			return_str += format_face(face) + '\n'
	else:
		for face in faces:
			return_str += format_face(face, format_str) + '\n'
	return return_str[:-1]

def format_face(face_dict, format_str='%{name} %{mana_cost}\n%{oracle_text}\n`"%{flavor_text}"`\n`%{power}/%{toughness}\n`'):
	cond_incl = re.compile(r'`([^`]*)`', re.MULTILINE)
	r = re.compile(r'%{([^}]*)}', re.MULTILINE)

	return_str = format_str
	while(True):
		match = cond_incl.search(return_str)
		if match == None:
			break
		sub_str_orig = match.group(1)
		sub_str = sub_str_orig
		incl = True
		while(True):
			sub_match = r.search(sub_str)
			if sub_match == None:
				break
			sub_key = sub_match.group(1)
			if sub_key in face_dict.keys():
				sub_value = face_dict[sub_key]
			else:
				incl = False
				break
			sub_str = re.sub('%{' + sub_key + '}', sub_value, sub_str)
		if incl:
			return_str = re.sub('`' + sub_str_orig + '`', sub_str, return_str)
		else:
			return_str = re.sub('`' + sub_str_orig + '`', '', return_str)
	while(True):
		m = r.search(return_str)
		if m == None:
			return return_str
		key = m.group(1)
		if key in face_dict.keys():
			value = face_dict[key]
		else:
			value = ''
		return_str = re.sub('%{' + key + '}', value, return_str)
		
