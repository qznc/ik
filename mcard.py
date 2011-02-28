#!/usr/bin/env python
import hashlib

"""
Key Spec:

A "contact" is usually a person, but could also be a bot, an organization,
a group, or an identity.

name: Full name of a contact
   ,business: Full formal name with titles etc. as you would write it on your card.
   ,private: Casual name, as you name your friends in your phonebook.
email: Emailaddress in its shortest format as websites would accept it.
   Emails are assumed to be unique.
   ,business:
   ,private:
phone: Phonenumber, usually in international format.
   ,business:
   ,private:
post address: Usually street, house number, city, zip code, and country.
gender: Usually male or female.
portrait: URL of an portrait image.
: Reuse the key before.
"""

VERSION = 1
DEFAULT_ENCODING = "utf8"

def load_file(path):
   fh = open(path, 'rb')
   line = fh.readline()
   ident,version,encoding = line.decode("ascii").split(" ")
   assert ident == "mcard"
   version = int(version)
   assert version == VERSION
   d = parse_file(fh, version, encoding)
   fh.close()
   return d
   fh.close()

def _parse_line(line, last=None):
   try:
      i = line.rindex(":")
   except ValueError:
      return None, None
   key = line[:i].strip()
   if not key:
      assert(last)
      key = last
   value = line[i+1:].strip()
   return key,value

def parse_file(f, version=VERSION, encoding=DEFAULT_ENCODING):
   last_key = None
   text = ""
   props = dict()
   while True:
      line = f.readline().decode(encoding)
      if not line: break
      key,value = _parse_line(line, last=last_key)
      if not key:
         assert(value is None)
         text = f.read().decode(encoding).strip()
         break
      else:
         props[key] = value
      last_key = key
   return MCard(props, text)

class MCard:
   def __init__(self, props, text=""):
      self.props = props
      self.text = text
   def __str__(self):
      string = ""
      for kv in self.props.items():
         string += "%s:%s\n" % kv
      string += "\n"
      string += self.text
      return string
   def __getitem__(self, key):
      try:
         return self.props[key]
      except KeyError, e:
         for k in self.props.keys():
            if k.startswith(key+","):
               return self.props[k]
         raise e
   def __setitem__(self, key, value):
      self.props[key] = value
   def get(self, key, default):
      try:
         return self.__getitem__(key)
      except KeyError:
         return default
   def store(self, sdir):
      string = str(self).encode(DEFAULT_ENCODING)
      hsh = hashlib.sha256(string).hexdigest()
      filename = hsh + ".mcard"
      # create an temporary dot file
      tmppath = os.path.join(sdir, "."+filename)
      fh = open(tmppath, 'w')
      fh.write("mcard %d %s\n" % (VERSION, DEFAULT_ENCODING))
      fh.write(string)
      fh.close()
      path = os.path.join(sdir, filename)
      os.rename(tmpf, path)
      return path

import xapian

class Database:
   def __init__(self, path):
      self._db = xapian.WritableDatabase(path, xapian.DB_CREATE_OR_OPEN)
   def index(self, directory):
      indexer = xapian.TermGenerator()
      stemmer = xapian.Stem("english")
      indexer.set_stemmer(stemmer)
      for p in iglob("%s/*.mcard" % directory):
         mcard = load_file(p)
         doc = xapian.Document()
         doc.set_data(p)
         indexer.set_document(doc)
         indexer.index_text_without_positions(mcard.text)
         for k,v in mcard.props.items():
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
      return set([m.document.get_data() for m in matches])

if __name__ == "__main__":
   from glob import iglob
   for p in iglob("tests/*.mcard"):
      c = load_file(p)
   db = Database("xapian.db")
   db.index("tests")
   me = load_file(db.search("zwin*").pop())
   print me["name,business"]
