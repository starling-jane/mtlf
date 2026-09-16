#!/usr/local/bin/python3.15

import mtlf
import scroller

# hello! this is a curses-based commandline client for browsing
# cards. it's not documented elsewhere because it's in a very
# early state and i'm unsure how much i want to continue
# developing it.

# feel free to use it, but consider it unsupported!
# requires scroller.py
# won't install onto your base system, but if your working
# directory is the base directory of this repository, you should
# be able to run this program from there

class Client:
	def __init__(self):
		self.cards = mtlf.Cards_dict()
		self.filename = None
		self.last_query = ''
		self.last_tags = ''
		self.sort = None

		self.scroller = scroller.Scroller(mgk.print_card, self.cli_callback, self.key_callback)

	def search_cards(self, query):
		self.last_query = query
		results = self.cards.search_jsons(query, self.sort)
		feedback = str(len(results)) + " matches."
		return feedback, results

	def sortby(self, args):
		pair = args.split(' ')
		sort = pair[0]
		reverse = False
		feedback = 'sorting by ' + pair[0] + ' ascending'
		if len(pair) > 1:
			if pair[1].lower() == 'desc':
				reverse = True
				feedback = 'sorting by ' + pair[0] + ' descending'
		self.sort = (sort, reverse)
		_, results = self.search_cards(self.last_query)
		return feedback, results
	
	def write_file(self, args):
		self.filename = args
		return 'writing to ' + self.filename, None
	
	def tags(self, args):
		if args != '':
			self.last_tags = args
		return 'tagged with ' + self.last_tags, None
	
	def unknown(self, args):
		return 'unknown command', None
	
	def cli_callback(self, query):
		pair = query.split(' ', 1)
		command = pair[0]
		if len(pair) > 1:
			args = pair[1]
		else:
			args = ''
		match command:
			case 's' | 'search':
				return self.search_cards(args)
			case 'w' | 'write':
				return self.write_file(args)
			case '#':
				return self.tags(args)
			case 'sort':
				return self.sortby(args)
			case _:
				return self.unknown(args)
	
	def key_callback(self, key, json):
		return "unknown keypress"


Client()
