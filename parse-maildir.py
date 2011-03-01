#!/usr/bin/env python
import os
import sys
from glob import iglob
import email.header

from mcard import MCard, load_file
from mcarddb import CardHolder

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

def insert(full_addr, holder):
   if not full_addr: return
   name, addr = parseaddr(full_addr)
   if not addr: return
   card = MCard()
   if name:
      card["name"] = name
   card["email"] = addr
   holder.store(card)
   print "Added:", name, addr

if __name__ == "__main__":
   maildir, outputdir = sys.argv[1:]
   maildir = os.path.abspath(maildir)
   outputdir = os.path.abspath(outputdir)
   holder = CardHolder(outputdir)
   for p in iglob(maildir+"/*"):
      mail = email.message_from_file(open(p))
      insert(mail["From"], holder)
      insert(mail["To"], holder)

