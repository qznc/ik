import curses
import locale
locale.setlocale(locale.LC_ALL,"")

import ncards

ENTER = ord("\n")

def draw(screen, string, cards):
   my, mx = screen.getmaxyx()
   for i in range(0,my-2):
      if i < len(cards):
         card = cards[-i]
         name = card.get("name")
         if not name:
            name = card.get("email", "?")
         line = name.encode("utf8")
         screen.addstr(i+1, 1, line+"\n")
      else:
         screen.addstr("\n")
   screen.addstr(0, 0, "\n") # clear line
   screen.addstr(0, 0, "> "+string.encode("utf8"))
   screen.refresh()

def search(string, cards):
   res = cards
   for query in string.split():
      res = list(ncards.search(res, query))
   return res

def app(screen, all_cards):
   encoding = "utf8"
   string = ""
   cards = []
   draw(screen, string, cards)
   try:
      while True:
         ch = screen.getch()
         if   ch == curses.KEY_EXIT:
            break
         elif ch == curses.KEY_BACKSPACE:
            string = string.decode(encoding)[:-1].encode(encoding)
         elif ch == ENTER:
            pass # TODO
         elif ch < 128:
            string += chr(ch)
         elif ch < 256:
            string += chr(ch)
            try:
               string.decode(encoding)
            except UnicodeDecodeError:
               # read one more char
               continue
         else:
            pass # TODO
         ustring = string.decode("utf8")[:20]
         cards = search(ustring, all_cards)
         draw(screen, ustring, cards)
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
