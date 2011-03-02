#!/usr/bin/env python
import os
from glob import iglob
import xapian
from mcard import load_file, parse_string
from blobdb import IndexedDatabase

class CardHolder:
   def __init__(self,path,readonly=False):
      self.path = path
      self._db = IndexedDatabase(path,readonly=readonly)
   def search(self,query):
      for cid in self._db.search(query):
         yield cid
   def get(self,cid):
      return parse_string(self._db.get(cid))
   def put(self,card):
      def extract(indexer, dummy):
         indexer.index_text(card.text)
         for k,v in card.items():
            indexer.index_text(v)
      return self._db.put(str(card), extract=extract)
   def delete(self, cid):
      self._db.delete(cid)

