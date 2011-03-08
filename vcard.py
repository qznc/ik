from mcard import MCard
import quopri
import base64

def _read_vcard(fh):
   card = dict()
   line = fh.readline()
   while line:
      line = line.strip()
      if line == "END:VCARD":
         return card
      i = line.index(":")
      key = line[:i].lower().strip()
      val = line[i+1:].strip()
      keys = key.split(";")
      encoding = "ascii"
      if keys[-1].startswith("charset="):
         encoding = keys.pop().split("=")[1]
      if keys[-1].startswith("encoding="):
         code = keys.pop().split("=")[1]
         if code == "quoted-printable":
            while val.endswith("="):
               val = val[:-1] + fh.readline().strip()
            val = quopri.decodestring(val)
         elif code == "base64":
            val = ""
            line = fh.readline().strip()
            while line:
               val += line
               line = fh.readline().strip()
            val = base64.decodestring(val)
      if keys[0] == "photo":
         line = fh.readline()
         continue
      key = ",".join(keys)
      if not key in card:
         card[key] = list()
      card[key].append(val.decode(encoding))
      line = fh.readline()

_KEY_TRANSLATE = {
   "fn": "name",
   "email,internet": "email",
   "email,internet,home": "email,private",
   "email,internet,work": "email,business",
   "tel":               "phone",
   "tel,voice,cell":    "phone",
   "tel,cell":          "phone",
   "tel,voice":         "phone",
   "tel,home":             "phone,private",
   "tel,home,voice":       "phone,private",
   "tel,home,voice,cell":  "phone,private",
   "tel,work":             "phone,business",
   "tel,work,voice":       "phone,business",
   "tel,work,voice,cell":  "phone,business",
   "tel,work,fax": "fax,business",
   "tel,fax": "fax",
   "url":      "web",
   "url,work": "web,business",
   "url,home": "web,private",
   "adr,home": "address,private",
   "adr,work": "address,business",
}
_IGNORE_KEYS = "uid title version rev n".split()

def vcard2mcard(vcard):
   """Converts an vcard to mcard with information loss"""
   mc = MCard()
   for k,vs in vcard.items():
      if k in _KEY_TRANSLATE:
         key = _KEY_TRANSLATE[k]
         for v in vs:
            mc[key] = v
      elif k.startswith("note"):
         mc.text = (mc.text + "\n" + "\n".join(vs)).strip()
      elif k.startswith("org"):
         for v in vs:
            def nonempty(string):
               return len(string) != 0
            org = " ".join(filter(nonempty, v.split(";")))
            mc["org"] = org
      elif k in _IGNORE_KEYS:
         pass
      else:
         print "Unknown vcard key", k, vs
   return mc

def read_file(path):
   """Reads a vcf file and returns vcard objects"""
   vcards = list()
   fh = open(path)
   line = fh.readline()
   while line:
      line = line.strip()
      if line == "BEGIN:VCARD":
         c = _read_vcard(fh)
         if c:
            vcards.append(c)
      else:
         print "Cannot handle line:", line
      line = fh.readline()
   return vcards

if __name__ == "__main__":
   import sys
   path = sys.argv[1]
   cards = read_file(path)
   for c in cards:
      print vcard2mcard(c)
