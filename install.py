import os 

homedir = os.environ['HOME']
cdir = os.getcwd()

print(cdir)

with open(f"{homedir}/.bash_aliases","a") as f:
    f.write(f"\nalias rst2tex='python3 {cdir}/rst2tex.py'")

