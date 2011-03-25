#!/usr/bin/env python
import sys
import os
import email.header
from glob import iglob

import vcard
import ncards
from ncard import NCard

_DBFILE="contacts.ciff"
_USAGE="""\
Usage: %s <cmd> ...
where <cmd> is one of: search, show, merge, import-maildir
""" % sys.argv[0]

def do_search(args):
   fh = open(_DBFILE)
   res = list(ncards.read(fh))
   fh.close()
   for query in args:
      res = ncards.search(res, query)
   for card in res:
      name = card.get("name")
      if not name:
         name = card.get("email", "?")
      print "%5d %s" % (card.id, name)

def do_show(args):
   index = int(args[0])
   fh = open(_DBFILE)
   res = ncards.read(fh)
   for card in ncards.read(fh):
      if card.id == index:
         print card
   fh.close()

def do_merge(args):
   fh = open(_DBFILE)
   cards = list(ncards.read(fh))
   fh.close()
   ids = map(int,args)
   mergeset = [c for c in cards if c.id in ids]
   new = ncards.merge(mergeset)
   ncards.remove(cards, ids)
   cards.append(new)
   fh = open(_DBFILE, 'w')
   ncards.save(fh, cards)
   fh.close()

def _decode_name(string):
   parts = email.header.decode_header(string)
   name = ""
   for data, encoding in parts:
      if encoding:
         name += data.decode(encoding)
      else:
         name += data.decode("ascii", "ignore")
   name = unicode(name)
   for c in u"\"'":
      if name.startswith(c) and name.endswith(c):
         name = name[1:-1]
   name = name.replace("  ", " ")
   return name

def _extract_maildir_addresses(maildir):
   for p in iglob(maildir+"/*"):
      mail = email.message_from_file(open(p))
      fields = list()
      for f in ("From", "To", "Cc", "Bcc"):
         if mail[f]:
            fields.append(mail[f])
      addresses = email.utils.getaddresses(fields)
      for x in addresses:
         yield x

def _insert(cards):
   fh = open(_DBFILE)
   original = list(ncards.read(fh))
   fh.close()
   cards = ncards.insert(original[:], cards)
   fh = open(_DBFILE, 'w')
   ncards.save(fh, cards)
   fh.close()

def do_import_maildir(args):
   cards = list()
   maildir = os.path.abspath(args[0])
   for name,addr in _extract_maildir_addresses(maildir):
      card = NCard()
      card.add("name", _decode_name(name))
      card.add("email", addr.decode("ascii", "ignore"))
      cards.append(card)
   _insert(cards)

def do_import_vcf(args):
   vcfpath = args[0]
   for vc in vcard.read_file(vcfpath):
      mc = vcard.vcard2mcard(vc)
      cid = holder.put(mc)
      # try to merge with already existing contacts:
      m = set([cid])
      for adr in mc.getAll("email"):
         results = set(holder.search(adr))
         m.update(results)
      if len(m) > 1:
         _merge(m,holder)

def do_my_index(args):
   cards = list()
   holder = CardHolder(_BASE)
   for cid in holder:
      card = holder.get(cid)
      cards.append(card)
   from radixtree import radixdict
   from time import time
   d = radixdict()
   start = time()
   for card in cards:
      for k,v in card.items():
         for vp in v.split():
            d.insert(vp,card)
      for word in card.text.split():
         d.insert(word,card)
   print "everything indexed in", time() - start, "seconds"

def main(args):
   cmd = args.pop(0)
   cmd = cmd.replace("-", "_")
   try:
      func = globals()["do_"+cmd]
   except KeyError:
      print _USAGE
      return
   func(args)


if __name__ == "__main__":
   main(sys.argv[1:])
