class NCard(list):
   def get(self, key, default=None):
      for k,v in self:
         if k==key:
            return v
      return default
   def add(self, key, value):
      for k,v in self:
         if k==key and v==value:
            return
      self.append((key,value))
   def __str__(self):
      res = ""
      idn = self.id
      res += "%d:\n" % idn
      for k,v in self:
         res += "%12s: %s\n" % (k,v)
      return res[:-1]

