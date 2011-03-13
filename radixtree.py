class KeySuffixError(KeyError):
   pass

class radixdict:
   def __init__(self):
      self._subtrees = list()
      self._items = list()
   def insert(self, key, item):
      """Insert item into tree"""
      if not key:
         self._items.append(item)
         return
      first = key[0]
      for c in self._subtrees:
         k,subtree = c
         if k[0] == first:
            if k == key[:len(k)]:
               inner_key = key[len(k):]
               subtree.insert(inner_key,item)
               return
            else: # split c
               common_key = key[:len(k)]
               key_rest_new = key[len(common_key):]
               key_rest_old = k  [len(common_key):]
               sub = radixdict()
               sub._subtrees.append((key_rest_old, subtree))
               sub.insert(key_rest_new,item)
               self._subtrees.append((common_key,sub))
               # remove obsolete stuff
               self._subtrees.remove(c)
               return
      # insert single subtree
      sub = radixdict()
      sub.insert("",item)
      self._subtrees.append((key,sub))
   def get(self, key):
      """Returns all _items, whose key is `key`"""
      try:
         subtree = self._getSubtree(key)
         return subtree._items
      except KeySuffixError:
         return []
   def getAll(self, key):
      """Returns all _items, whose key starts with `key`"""
      if not key:
         res = self._items[:]
         for k,s in self._subtrees:
            res.extend(s.getAll(None))
         return res
      try:
         subtree = self._getSubtree(key)
         return subtree.getAll(None)
      except KeySuffixError:
         return []
   def removeKey(self, key):
      """Remove all entries, whose key is `key`"""
      subtree = self._getSubtree(key)
      subtree._items = list()
   def removeKeyAll(self, key):
      """Remove all entries, whose key starts with `key`"""
      subtree = self._getSubtree(key)
      subtree._items = list()
      subtree._subtrees = list()
   def _getSubtree(self, key):
      if not key:
         return self
      first = key[0]
      for k,subtree in self._subtrees:
         if k[0] == first:
            inner_key = key[len(k):]
            return subtree._getSubtree(inner_key)
      raise KeySuffixError(key)
   def __repr__(self):
      return "<radixdict %s %s>" % (self._items, self._subtrees)

if __name__ == "__main__":
   d = radixdict()
   d.insert("blub", 3)
   d.insert("blubber", 4)
   d.insert("blub", 5)
   d.insert("blu", 6)
   d.insert("blue", 7)
   d.insert("blubb", 8)
   print d
   print d.get("blub")
   print d.getAll("blub")
   d.removeKey("blub")
   print d.getAll("blub")
   d.removeKeyAll("blub")
   print d.getAll("blub")
