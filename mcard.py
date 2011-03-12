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
address: Usually street, house number, city, zip code, and country.
web: homepage, website, etc.
   ,business:
   ,private:
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
   card = MCard()
   while True:
      line = f.readline().decode(encoding)
      if not line: break
      key,value = _parse_line(line, last=last_key)
      if not key:
         assert(value is None)
         card.text = f.read().decode(encoding).strip()
         break
      else:
         card[key] = value
      last_key = key
   return card

class FakeFile:
   def __init__(self, string):
      self.string = string
      self.i = 0
   def readline(self):
      s = i = self.i
      while True:
         if i==len(self.string):
            return self.string[s:]
         if self.string[i] == "\n":
            self.i = i+1
            return self.string[s:i]
         i+=1

def parse_string(string):
   i = string.index("\n")
   mt, version, encoding = string[:i].split()
   version = int(version)
   data = string[i+1:]
   fdata = FakeFile(data)
   return parse_file(fdata, version, encoding)

class MCard:
   def __init__(self, props=None, text=""):
      if not props:
         props = set()
      self._props = props
      self.text = text
   def __str__(self):
      string = u""
      string += "mcard %d %s\n" % (VERSION, DEFAULT_ENCODING)
      ps = list(self._props)
      ps.sort()
      for kv in ps:
         string += "%s:%s\n" % kv
      string += "\n"
      string += self.text
      return string.encode(DEFAULT_ENCODING)
   def __getitem__(self, key):
      key = key.encode("ascii")
      for k,v in self._props:
         if k == key:
            return v
      for k,v in self._props:
         if k.startswith(key+","):
            return v
      raise KeyError(key)
   def __setitem__(self, key, value):
      self._props.add((key,value))
   def get(self, key, default):
      try:
         return self.__getitem__(key)
      except KeyError:
         return default
   def items(self):
      for x in self._props:
         yield x
   def getAll(self, key):
      for k,v in self._props:
         if k==key or k.startswith(key+","):
            yield v

