import curses
import locale
locale.setlocale(locale.LC_ALL,"")

import ncards

ENTER = ord("\n")

def draw(screen, string, cards, pos):
   my, mx = screen.getmaxyx()
   for i in range(0,my-2):
      if i < len(cards):
         card = cards[-i]
         name = card.get("name")
         if not name:
            name = card.get("email", "?")
         line = name.encode("utf8")
         if i+1 == pos:
            screen.addstr(i+1, 1, line+"\n", curses.A_REVERSE)
         else:
            screen.addstr(i+1, 1, line+"\n")
      else:
         screen.addstr("\n")
   screen.addstr(0, 0, "\n") # clear line
   screen.addstr(0, 0, "> "+string.encode("utf8"))
   if pos == 0:
      curses.curs_set(2)
   else:
      curses.curs_set(0)
   screen.refresh()

def show_card(screen, card):
   my, mx = screen.getmaxyx()
   keylen = 0
   count = 0
   for k,v in card:
      keylen = max(keylen, len(k)+2)
      count = min(my-6,count+1)
   win = screen.subwin(count+2,mx-6,2,3)
   win.addstr(0,0,"")
   win.erase()
   y,x = win.getyx()
   y += 1
   win.border(0)
   for k,v in list(card)[:count]:
      win.addstr(y,1,k)
      win.addstr(y,keylen,v.encode("utf8"))
      y += 1

def search(string, cards):
   res = cards
   for query in string.split():
      res = list(ncards.search(res, query))
   return res

def app(screen, all_cards):
   my, mx = screen.getmaxyx()
   encoding = "utf8"
   string = ""
   cards = []
   selected = 0 # selected row on screen
   draw(screen, string, cards, selected)
   try:
      while True:
         ch = screen.getch()
         if   ch == curses.KEY_EXIT:
            break
         elif ch == curses.KEY_BACKSPACE:
            string = string.decode(encoding)[:-1].encode(encoding)
         elif ch == curses.KEY_DOWN:
            selected = min(my-2, selected+1, len(cards))
         elif ch == curses.KEY_UP:
            selected = max(0, selected-1)
         elif ch == ENTER and selected == 0:
            selected = 1
         elif selected == 0: # search string entering
            assert 13 < ch < 256
            string += chr(ch)
            try:
               string.decode(encoding)
            except UnicodeDecodeError:
               # read one more char
               continue
         elif chr(ch) in "sS":
            selected = 0
         elif chr(ch) in "qQxX":
            break
         else:
            pass # TODO
         ustring = string.decode("utf8")[:20]
         cards = search(ustring, all_cards)
         draw(screen, ustring, cards, selected)
         if ch == ENTER and selected > 0:
            show_card(screen, cards[-selected+1])
   except KeyboardInterrupt:
      pass

class CursesUI:
   def __init__(self, cards):
      self.cards = list(cards)
   def start(self):
      curses.wrapper(self._curses_app)
   def _curses_app(self, scr):
      app(scr, self.cards)

if __name__ == "__main__":
   curses.wrapper(app)
