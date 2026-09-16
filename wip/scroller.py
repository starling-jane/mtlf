import curses

def main(stdscr):
	stdscr.clear()

	height = curses.LINES
	width = curses.COLS
	while True:
		key = stdscr.getkey()
		stdscr.clear()
		stdscr.addstr(0, 0, key)
		stdscr.refresh()
		if key == 'q':
			break

class Scroller:
	def curses_loop(self, scr):
		self.scr = scr
		self.scr.clear()

		self.height = curses.LINES
		self.width = curses.COLS

		self.scroll = 0
		self.selected = 0
		self.printhead = 0
		
		curses.curs_set(0)

		curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
		self.color_normal = curses.color_pair(1)
		self.color_highlight = curses.color_pair(2)

		self.feedback = ''
		while True:

			self.scr.clear()
			i = self.scroll
			self.printhead = 0
			while self.print_item(i):
				i += 1

			self.scr.addstr(self.height - 1, 0, self.feedback, self.color_highlight)
			self.feedback = ''
			self.scr.refresh()

			key = self.scr.getkey()
			if key == ':':
				self.scr.addstr(self.height - 1, 0, ':' + (' ' * (self.width - 2)))
				i = bytes.decode(self.get_input(), 'utf-8')
				self.feedback, data = self.cli_callback(i)
				if data != None:
					self.selected = 0
					self.scroll = 0
					self.items = []
					for datum in data:
						self.add_item(datum)
			elif key == 'q':
				break
			elif key == 'KEY_DOWN':
				self.selected += 1
			elif key == 'KEY_UP':
				self.selected -= 1
			else:
				self.feedback = self.key_callback(key, self.items[self.selected])
			if self.selected < 0:
				self.selected = 0
			if self.selected > len(self.items) - 1:
				self.selected = len(self.items) - 1
			self.scroll += self.in_bounds()

	def in_bounds(self):
		j = self.scroll
		accumulated_height = self.items[j].height
		if j > self.selected:
			return -1
		while True:
			if accumulated_height > self.height:
				return 1
			elif j == self.selected:
				return 0
			accumulated_height += self.items[j].height
			j += 1
	def print_item(self, i):
		if i < len(self.items):
			if len(self.items[i].lines) < self.height - self.printhead:
				if i == self.selected:
					color = self.color_highlight
				else:
					color = self.color_normal
				for j in range(len(self.items[i].lines)):
					self.scr.addstr(self.printhead + j, 0, self.items[i].lines[j], color)
				self.printhead += j
				return True
			else:
				return False
		else:
			return False
	def get_input(self):
		curses.echo()
		curses.curs_set(1)
		s = self.scr.getstr(self.height - 1, 1)
		curses.noecho()
		curses.curs_set(0)
		return s
	def __init__(self, printer, cli_callback, key_callback):
		self.width = 40
		self.height = 40
		self.items = []
		self.printer = printer
		self.cli_callback = cli_callback
		self.key_callback = key_callback
		curses.wrapper(self.curses_loop)
	def add_item(self, data):
		self.items.append(ScrollerItem(data, self.printer, self.width))

class ScrollerItem:
	def __init__(self, data, printer, width):
		self.data = data
		self.text = printer(data)
		
		self.lines = self.text.split("\n")
		i = 0
		while i < len(self.lines):
			if len(self.lines[i]) > width:
				self.lines.insert(i+1, self.lines[i][width:])
				self.lines[i] = self.lines[i][:width]
			i = i + 1
		self.height = len(self.lines)
