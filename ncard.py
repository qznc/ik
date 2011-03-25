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
      self.append((unicode(key),unicode(value)))
   def matches(self, card):
      """Whether the other card represents the same person"""
      for k1,v1 in self:
         if k1.startswith("email"):
            for k2,v2 in card:
               if k2.startswith("email") and v1==v2:
                  return True
      return False
   def __str__(self):
      res = ""
      idn = getattr(self, "id", -1)
      res += u"%d:\n" % idn
      for k,v in self:
         res += u"%12s: %s\n" % (k,v)
      return res[:-1]

