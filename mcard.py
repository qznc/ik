#!/usr/bin/env python
import hashlib
import os
from glob import iglob

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
   def __init__(self, props=None, text=""):
      if not props:
         props = dict()
      self.props = props
      self.text = text
   def __str__(self):
      string = u""
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
   def getAll(self, key):
      for k in self.props.keys():
         if k==key or k.startswith(key+","):
            yield self.props[k]
   def store(self, sdir):
      string = self.__str__().encode(DEFAULT_ENCODING)
      hsh = hashlib.sha256(string).hexdigest()
      filename = hsh + ".mcard"
      # create an temporary dot file
      tmppath = os.path.join(sdir, "."+filename)
      fh = open(tmppath, 'w')
      fh.write("mcard %d %s\n" % (VERSION, DEFAULT_ENCODING))
      fh.write(string)
      fh.close()
      path = os.path.join(sdir, filename)
      os.rename(tmppath, path)
      return path

