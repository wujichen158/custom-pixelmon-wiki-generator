import os
import json
'''for root, ds, fs in os.walk("C:\\Users\\asus\\Desktop\\moves"):
	print(root)
	for d in ds:
		print(d)
	for f in fs:
		print(f)'''
	

def processDirs(dirs):
	resStr = """{{#switch:{{{2|}}}
|??0x? Crash={{MoveLevel|{{{1|1}}}|??0x? Crash|Normal|Special|80|100|10|{{#switch: {{{3}}}|bold|stab='''|italic=''|{{{3|}}}}}}}"""
	for f in dirs:
		if f.endswith(".json"):
			resStr += genMoveString(readMoveFile(f))
	resStr += """
|#default={{MoveLevel|{{{1|1}}}|Error|Unknown|Status|Error|Error|Error[[Category:Typos in moveset]]|}}
}}<noinclude>[[Category:Learnlist templates]]{{documentation}}</noinclude>"""
	return resStr
			
def genMoveString(data):
	attackName = data['attackName']
	attackType = data['attackType'].capitalize()
	attackCategory = data['attackCategory'].capitalize()
	basePower = ("—" if data['attackCategory'] == "STATUS" or data['basePower'] <= 0 else str(data['basePower']))
	accuracy = ("—" if data['accuracy'] <=0 else str(data['accuracy']))
	ppBase = str(data['ppBase'])
	suffix = ("" if data['attackCategory'] == "STATUS" or data['basePower'] <= 0 else "|{{#switch: {{{3}}}|bold|stab='''|italic=''|{{{3|}}}}}")
	
	resStr = """
|""" + attackName + "={{MoveLevel|{{{1|1}}}|" + attackName + "|" + attackType + "|" + attackCategory + "|" + basePower + "|" + accuracy + "|" + ppBase + suffix + "}}"
	return resStr
		
def readMoveFile(moveName):
	with open("moves/" + moveName, 'r', encoding='utf-8') as f:
		data = json.load(f)
		return data

if __name__ == '__main__':
	dirs = os.listdir("moves")
	print(processDirs(dirs))