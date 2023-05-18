MSG = input("Pasa fiera? ")
text = "Hola mundo! " + MSG
with open('out/result', 'w') as f:
	f.write(text)
print(text)
