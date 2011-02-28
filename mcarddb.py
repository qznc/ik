#!/usr/bin/env python
import os
from glob import iglob
import xapian
from mcard import load_file

class IndexDatabase:
   def __init__(self, path):
      self._db = xapian.WritableDatabase(path, xapian.DB_CREATE_OR_OPEN)
   def index(self, directory):
      indexer = xapian.TermGenerator()
      stemmer = xapian.Stem("english")
      indexer.set_stemmer(stemmer)
      for p in iglob("%s/*.mcard" % directory):
         self.indexFile(p)
   def indexFile(self, p, indexer=None):
      if not indexer:
         indexer = xapian.TermGenerator()
         stemmer = xapian.Stem("english")
         indexer.set_stemmer(stemmer)
      mcard = load_file(p)
      doc = xapian.Document()
      doc.set_data(p)
      indexer.set_document(doc)
      indexer.index_text_without_positions(mcard.text)
      for k,v in mcard.items():
         indexer.index_text_without_positions(v)
      self._db.add_document(doc)
   def search(self, query):
      enquire = xapian.Enquire(self._db)
      qp = xapian.QueryParser()
      stemmer = xapian.Stem("english")
      qp.set_stemmer(stemmer)
      qp.set_database(self._db)
      qp.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
      query = qp.parse_query(query, xapian.QueryParser.FLAG_WILDCARD)
      enquire.set_query(query)
      matches = enquire.get_mset(0, 10)
      for m in matches:
         path = m.document.get_data()
         if os.path.exists(path):
            yield path
         else:
            m.document.clear_values()

class CardHolder:
   def __init__(self,path):
      self.path = path
      self.indexdb = IndexDatabase(os.path.join(path,"indexdb"))
   def search(self,query):
      for p in self.indexdb.search(query):
         cid = os.path.basename(p)[:-6]
         yield cid
   def load(self,cid):
      return load_file(self._cid2path(cid))
   def store(self,card):
      path = card.store(self.path)
      self.indexdb.indexFile(path)
   def update_index(self):
      self.indexdb.index(self.path)
   def delete(self, cid):
      os.remove(self._cid2path(cid))
   def _cid2path(self, cid):
      return os.path.join(self.path, cid+".mcard")

