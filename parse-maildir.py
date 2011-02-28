#!/usr/bin/env python
import os
import sys
from glob import iglob
import email.header

from mcard import MCard, load_file
from mcarddb import IndexDatabase

def parseaddr(mailaddr):
   comment, addr = email.Utils.parseaddr(mailaddr)
   parts = email.header.decode_header(comment)
   name = ""
   for data, encoding in parts:
      if encoding:
         name += data.decode(encoding)
      else:
         name += data
   return name, addr

def insert(full_addr, db, outputdir):
   if not full_addr: return
   name, addr = parseaddr(full_addr)
   if not addr: return
   results = list(db.search(addr))
   if len(results) > 0:
      for p in results:
         card = load_file(p)
         for paddr in card.getAll("email"):
            if paddr == addr:
               return # already there
   card = MCard()
   if name:
      card["name"] = name
   card["email"] = addr
   path = card.store(outputdir)
   db.indexFile(path)
   print "Added:", name, addr

if __name__ == "__main__":
   maildir, outputdir, dbdir = sys.argv[1:]
   maildir = os.path.abspath(maildir)
   outputdir = os.path.abspath(outputdir)
   dbdir = os.path.abspath(dbdir)
   db = IndexDatabase(dbdir)
   for p in iglob(maildir+"/*"):
      mail = email.message_from_file(open(p))
      insert(mail["From"], db, outputdir)
      insert(mail["To"], db, outputdir)

