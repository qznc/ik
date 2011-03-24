#!/usr/bin/env python
import os
from glob import iglob
from mcard import MCard
from iff import read_iff

class CardHolder:
   def __init__(self,path,readonly=False):
      self.path = path
      self.cards = list()
      self._load_iff_file()
   def _load_iff_file(self):
      chunks = dict()
      fh = open(self.path)
      for name,data in read_iff(fh):
         chunks[name] = data
      fh.close()
      keys = chunks["KEYS"].split("\0")
      data = chunks["MCRD"]
      length = len(data)
      pos = 0
      cc = MCard()
      while pos < length:
         key = keys[ord(data[pos])]
         pos += 1
         if key == keys[0]:
            self.cards.append(cc)
            cc = MCard()
         else:
            end = data.index("\0", pos)
            cc[key] = data[pos:end].decode("utf8")
            pos = end+1
   def __iter__(self):
      return self._db.__iter__()
   def search(self,query):
      for cid in self._db.search(query):
         yield cid
   def _complete(self, cid_start):
      cids = list(self._db.completeIds(cid_start))
      if len(cids) > 1:
         raise Exception("Ambiguous cid: "+cid_start)
      elif len(cids) < 1:
         raise Exception("Unknown cid: "+cid_start)
      return cids[0]
   def get(self,cid):
      cid = self._complete(cid)
      return parse_string(self._db.get(cid))
   def put(self,card):
      def extract(indexer, dummy):
         indexer.index_text(card.text)
         for k,v in card.items():
            indexer.index_text(v)
      cid = self._db.put(str(card), extract=extract)
      return cid
   def delete(self, cid):
      cid = self._complete(cid)
      self._db.delete(cid)

if __name__ == "__main__":
   ch = CardHolder("blub")
