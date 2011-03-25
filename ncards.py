#!/usr/bin/env python
from ncard import NCard
from iff import read_iff, KeyIndexer, as_chunk

def read(fh):
   """Yields all cards read from a file"""
   chunks = dict()
   for name,data in read_iff(fh):
      chunks[name] = data
   fh.close()
   keys = chunks["KEYS"].split("\0")
   data = chunks["MCRD"]
   length = len(data)
   pos = 0
   count = 0
   cc = NCard()
   while pos < length:
      key = keys[ord(data[pos])]
      pos += 1
      if key == keys[0]:
         cc.id = count
         yield cc
         count += 1
         cc = NCard()
      else:
         end = data.index("\0", pos)
         cc.add(key, data[pos:end].decode("utf8"))
         pos = end+1

def save(fh, cards):
   """Write a list of cards to a file"""
   ki = KeyIndexer()
   end_key = ki.getIndex(" ")
   assert end_key == 0
   data = ""
   for card in cards:
      for k,v in card:
         i = ki.getIndex(k.encode("utf8"))
         data += chr(i)
         data += v.encode("utf8")
         data += "\0"
      data += chr(end_key)
   contacts = as_chunk("MCRD", data)
   keys = as_chunk("KEYS", ki.binary())
   full = as_chunk("FORM", keys+contacts)
   fh.write(full)

def search(cards, query):
   """Yield the cards matching the query"""
   for card in cards:
      for k,v in card:
         if query.lower() in v.lower():
            yield card
            break # next card

def remove(lst, ids):
   """Remove indices ids from card list lst"""
   # remove in reverse order to not change the indexes
   ids = sorted(map(int,ids),reverse=True)
   for id in ids:
      c = lst.pop(id)
      assert c.id == id

def merge(cards):
   """Merge a list of cards into one card"""
   new = NCard()
   for c in cards:
      for k,v in c:
         new.add(k,v)
   return new

def insert(cards1, cards2):
   """Merges both card lists and tries to merge individual cards in the process.
   cards2 is modified!"""
   result = list()
   # append all c1, but try to merge them before
   for c1 in cards1:
      matched = list()
      card = c1
      for c2 in cards2:
         if c1.matches(c2):
            matched.append(c2)
            card = merge([card,c2])
      if matched:
         for c2 in matched:
            cards2.remove(c2)
      result.append(card)
   # append remaining c2
   for c2 in cards2:
      result.append(c2)
   return result

