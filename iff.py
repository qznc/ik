from struct import pack

class KeyIndexer:
   def __init__(self):
      self.keys = list()
   def getIndex(self, key):
      for i,k in enumerate(self.keys):
         if k==key:
            return i
      i = len(self.keys)
      self.keys.append(key)
      return i
   def binary(self):
      data = ""
      for k in self.keys:
         data += k
         data += "\0"
      return data

def as_chunk(type,data):
   res = ""
   assert isinstance(type,str) and len(type) == 4
   length = pack(">i", len(data))
   assert isinstance(length,str) and len(length) == 4
   return type+length+data

