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

