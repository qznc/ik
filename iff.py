from struct import pack
from chunk import Chunk

def as_chunk(type,data):
   res = ""
   assert isinstance(type,str) and len(type) == 4
   length = pack(">i", len(data))
   assert isinstance(length,str) and len(length) == 4
   return type+length+data

def read_iff(fh,keys=["FORM"]):
   while True:
      try:
         ch = Chunk(fh, align=False)
      except EOFError:
         return
      name = ch.getname()
      if name == "FORM":
         typ = ch.read(4) # TODO return somehow
         for x in read_iff(ch):
            yield x
      else:
         data = ch.read(ch.getsize())
         yield name, data
