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
         cc.append((key, data[pos:end].decode("utf8")))
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
         if not isinstance(v,unicode):
            continue
         if query in v:
            yield card
            break # next card

def remove(cards, ids):
   # remove in reverse order to not change the indexes
   ids = sorted(map(int,ids),reverse=True)
   for id in ids:
      c = cards.pop(id)
      assert c.id == id

def merge(cards):
   new = NCard()
   for c in cards:
      for k,v in c:
         new.add(k,v)
   return new

