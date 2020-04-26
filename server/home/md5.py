import hashlib

code = hashlib.md5()

f = open("tree.py",'rb')
f_r = f.read()
print(f_r)
code.update(f_r)
with open("abc.txt",'w') as c:
    c.write(str(code.digest()))