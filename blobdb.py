#!/usr/bin/env python
import os.path
from glob import iglob
import hashlib

import xapian
from mcard import load_file

def string_extract(indexer, string):
   indexer.index_text(string)

class IndexedDatabase:
   def __init__(self, path):
      self.path = path
      if not os.path.isdir(path):
         os.makedirs(path)
      self.dbpath = os.path.join(path,"index.db")
      self._db = xapian.WritableDatabase(self.dbpath, xapian.DB_CREATE_OR_OPEN)
   def put(self, blob, extract=string_extract):
      ids = self._gen_ids(blob)
      self._storeBlob(blob, ids)
      self._indexBlob(blob, ids, extract=extract)
      return ids
   def get(self, ids):
      assert not ids.endswith(".blob")
      return open(self._gen_path(ids)).read()
   def _gen_ids(self, string):
      return hashlib.sha256(string).hexdigest()
   def _gen_path(self, ids):
      return os.path.join(self.path, ids+".blob")
   def _storeBlob(self, blob, ids):
      tmppath = os.path.join(self.path, "_tmp_"+ids)
      fh = open(tmppath, 'w')
      fh.write(blob)
      fh.close()
      path = os.path.join(self.path, ids+".blob")
      os.rename(tmppath, path)
   def _indexBlob(self, blob, ids, extract):
      self.delete(ids) # no duplicates!
      doc = xapian.Document()
      doc.add_term("Q"+ids)
      doc.set_data(ids)
      indexer = xapian.TermGenerator()
      stemmer = xapian.Stem("english")
      indexer.set_stemmer(stemmer)
      indexer.set_document(doc)
      extract(indexer, blob) # actual indexing in there
      self._db.add_document(doc)
   def _getDocument(self, ids):
      postlist = self._db.postlist("Q"+ids)
      try:
         plitem = postlist.next()
      except StopIteration:
         raise KeyError("No document with id "+ids)
      doc = self._db.get_document(plitem.docid)
      return doc
   def delete(self, ids):
      self._db.delete_document("Q"+ids)
   def search(self, query, count=100):
      enquire = xapian.Enquire(self._db)
      qp = xapian.QueryParser()
      stemmer = xapian.Stem("english")
      qp.set_stemmer(stemmer)
      qp.set_database(self._db)
      qp.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
      query = qp.parse_query(query, xapian.QueryParser.FLAG_WILDCARD)
      enquire.set_query(query)
      matches = enquire.get_mset(0, count)
      for m in matches:
         ids = m.document.get_data()
         path = self._gen_path(ids)
         if os.path.exists(path):
            yield ids
         else:
            m.document.clear_values()

if __name__ == "__main__":
   path = os.path.abspath("blob_testing")
   db = IndexedDatabase(path)
   ids = db.put("Hello World")
   print "data item:", ids
   results = list(db.search("Hello"))
   print "found:", results
