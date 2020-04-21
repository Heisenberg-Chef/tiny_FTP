import hashlib

code = hashlib.md5()

f = open("tree.py",'r')
f_r = f.read()
print(f_r)
code.update(f_r.encode())
with open("abc.txt",'w') as c:
    c.write(str(code.digest()))