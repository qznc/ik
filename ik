#!/usr/bin/env python
import sys
from mcarddb import CardHolder
from mcard import MCard

_BASE="/home/beza1e1/dev/mycontacts/tests"
_USAGE="""\
Usage: %s <cmd> ...
where <cmd> is one of: search, show, update-index, merge
""" % sys.argv[0]

def do_search(args):
   query = " ".join(args)
   holder = CardHolder(_BASE)
   results = holder.search(query)
   for cid in results:
      card = holder.load(cid)
      print cid, card.get("name", "?")

def do_show(args):
   holder = CardHolder(_BASE)
   print holder.load(args[0])

def do_update_index(args):
   holder = CardHolder(_BASE)
   holder.update_index()

def do_merge(args):
   cidA = args[0]
   cidB = args[1]
   holder = CardHolder(_BASE)
   cardA = holder.load(cidA)
   cardB = holder.load(cidB)
   cardC = MCard()
   cardC.props.update(cardA.props)
   cardC.props.update(cardB.props)
   cardC.text = cardA.text + "\n\b" + cardB.text
   holder.store(cardC)
   print cardC
   holder.delete(cidA)
   holder.delete(cidB)

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
