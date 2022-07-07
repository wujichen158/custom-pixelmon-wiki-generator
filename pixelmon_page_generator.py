import json
import string
import os

typeEffectList = [[1,1,1,1,1,0.5,1,0,0.5,1,1,1,1,1,1,1,1,1],
	[2,1,0.5,0.5,1,2,0.5,0,2,1,1,1,1,0.5,2,1,2,0.5],
	[1,2,1,1,1,0.5,2,1,0.5,1,1,2,0.5,1,1,1,1,1],
	[1,1,1,0.5,0.5,0.5,1,0.5,0,1,1,2,1,1,1,1,1,2],
	[1,1,0,2,1,2,0.5,1,2,2,1,0.5,2,1,1,1,1,1],
	[1,0.5,2,1,0.5,1,2,1,0.5,2,1,1,1,1,2,1,1,1],
	[1,0.5,0.5,0.5,1,1,1,0.5,0.5,0.5,1,2,1,2,1,1,2,0.5],
	[0,1,1,1,1,1,1,2,1,1,1,1,1,2,1,1,0.5,1],
	[1,1,1,1,1,2,1,1,0.5,0.5,0.5,1,0.5,1,2,1,1,2],
	[1,1,1,1,1,0.5,2,1,2,0.5,0.5,2,1,1,2,0.5,1,1],
	[1,1,1,1,2,2,1,1,1,2,0.5,0.5,1,1,1,0.5,1,1],
	[1,1,0.5,0.5,2,2,0.5,1,0.5,0.5,2,0.5,1,1,1,0.5,1,1],
	[1,1,2,1,0,1,1,1,1,1,2,0.5,0.5,1,1,0.5,1,1],
	[1,2,1,2,1,1,1,1,0.5,1,1,1,1,0.5,1,1,0,1],
	[1,1,2,1,2,1,1,1,0.5,0.5,0.5,2,1,1,0.5,2,1,1],
	[1,1,1,1,1,1,1,1,0.5,1,1,1,1,1,1,2,1,0],
	[1,0.5,1,1,1,1,1,2,1,1,1,1,1,2,1,1,0.5,0.5],
	[1,2,1,0.5,1,1,1,1,0.5,0.5,1,1,1,1,1,2,2,1]]
	
types = ["Normal","Fighting","Flying","Poison","Ground","Rock","Bug","Ghost","Steel","Fire","Water","Grass","Electric","Psychic","Ice","Dragon","Dark","Fairy"]

def getTypeNum():
	typeDict = {}
	for i, val in enumerate(types):
		typeDict[val] = i
	return typeDict
	
def readJSON(jsonPath):
	with open(jsonPath, 'r', encoding='utf-8') as f:
		data = json.load(f)
		return data

def processMoves():
	moveset = {}
	for f in os.listdir("moves"):
		move = {}
		if f.endswith(".json"):
			data = readJSON("moves/" + f)
			move['attackType'] = data['attackType'].capitalize()
			move['attackCategory'] = data['attackCategory'].capitalize()
			move['basePower'] = data['basePower']
			moveset[data['attackName']] = move
	return moveset

def processData(data, form, defaultForm, authors):
	moveset = processMoves()
	result = {}
	result['name'] = data['name']
	result['ndex'] = str(data['dex'])
	result['form'] = form
	pixelmonNew = {}
	hasDef = False
	for pixelmon in data['forms']:
		if pixelmon['name'] == defaultForm:
			savePixelmonAttributes(pixelmon, result)
			hasDef = True
		elif pixelmon['name'] == form.lower():
			if not hasDef:
				raise Exception("Custom forms should be written after the default form.")
			savePixelmonAttributes(pixelmon, result)
	# print(result)
	buildWikiStr(result, authors, moveset)

def savePixelmonAttributes(pixelmon, pixelmonNew):
	# types:
	if 'types' in pixelmon:
		# clear default values before filling
		pixelmonNew.pop('type2', None)
		pixelmonNew['type1'] = pixelmon['types'][0].capitalize()
		if len(pixelmon['types']) > 1:
			pixelmonNew['type2'] = pixelmon['types'][1].capitalize()

	# gender
	if 'possibleGenders' in pixelmon:
		if len(pixelmon['possibleGenders']) > 1:
			pixelmonNew['gendercode'] = "Female50Percent"
		else:
			pixelmonNew['gendercode'] = '255'
	
	# growth rate
	if 'experienceGroup' in pixelmon:
		pixelmonNew['growthrate'] = mapExpGroupName(pixelmon['experienceGroup'].replace('_', ' ').title())
		
	# exp yielding and friendship
	if 'spawn' in pixelmon:
		pixelmonNew['expyield'] = str(pixelmon['spawn']['baseExp'])
		pixelmonNew['friendship'] = str(pixelmon['spawn']['baseFriendship'])
	
	# ev earned
	if 'evYields' in pixelmon:
		pixelmonNew.pop('evYields', None)
		pixelmonNew['evYields'] = ""
		if 'hp' in pixelmon['evYields']:
			pixelmonNew['evYields'] += """
|evhp = """ + str(pixelmon['evYields']['hp'])
		if 'attack' in pixelmon['evYields']:
			pixelmonNew['evYields'] += """
|evat = """ + str(pixelmon['evYields']['attack'])
		if 'defense' in pixelmon['evYields']:
			pixelmonNew['evYields'] += """
|evde = """ + str(pixelmon['evYields']['defense'])
		if 'specialAttack' in pixelmon['evYields']:
			pixelmonNew['evYields'] += """
|evsa = """ + str(pixelmon['evYields']['specialAttack'])
		if 'specialDefense' in pixelmon['evYields']:
			pixelmonNew['evYields'] += """
|evsd = """ + str(pixelmon['evYields']['specialDefense'])
		if 'speed' in pixelmon['evYields']:
			pixelmonNew['evYields'] += """
|evsp = """ + str(pixelmon['evYields']['speed'])
	
	# catch rate
	if 'catchRate' in pixelmon:
		pixelmonNew['catchrate'] = str(pixelmon['catchRate'])
		
	# abilities
	if 'abilities' in pixelmon:
		pixelmonNew.pop('ability2', None)
		pixelmonNew.pop('hiddenability', None)
		if 'abilities' in pixelmon['abilities']:
			pixelmonNew['ability1'] = cutAbilityName(pixelmon['abilities']['abilities'][0])
			if len(pixelmon['abilities']['abilities']) > 1:
				pixelmonNew['ability2'] = cutAbilityName(pixelmon['abilities']['abilities'][1])
		if 'hiddenAbilities' in pixelmon['abilities'] and len(pixelmon['abilities']['hiddenAbilities']) > 0:
			pixelmonNew['hiddenability'] = cutAbilityName(pixelmon['abilities']['hiddenAbilities'][0])
	
	# egg groups
	if 'eggGroups' in pixelmon:
		pixelmonNew.pop('egggroup2', None)
		pixelmonNew['egggroup1'] = cutEggGroupName(pixelmon['eggGroups'][0])
		if pixelmonNew['egggroup1'] == 'Undiscovered':
			pixelmonNew['egggroup1'] = '0'
		if len(pixelmon['eggGroups']) > 1:
			pixelmonNew['egggroup2'] = cutEggGroupName(pixelmon['eggGroups'][1])
			
	# egg steps
	if 'eggCycles' in pixelmon:
		pixelmonNew['eggsteps'] = str(int(pixelmon['eggCycles']) * 256)
	
	# height. WARNING: not precise
	if 'dimensions' in pixelmon:
		pixelmonNew['height-m'] = str(pixelmon['dimensions']['height'])
		
	# weight
	if 'weight' in pixelmon:
		pixelmonNew['weight-kg'] = str(pixelmon['weight'])
	
	# species. Edit yourself
	pixelmonNew['species'] = 'Custom'
	
	# stats
	if 'battleStats' in pixelmon:
		pixelmonNew['Stats'] = ""
		pixelmonNew['Stats'] += ("""
|HP = """ + str(pixelmon['battleStats']['hp']) + """
|Attack = """ + str(pixelmon['battleStats']['attack']) + """
|Defense = """ + str(pixelmon['battleStats']['defense']) + """
|SpAtk = """ + str(pixelmon['battleStats']['specialAttack']) + """
|SpDef = """ + str(pixelmon['battleStats']['specialDefense']) + """
|Speed = """ + str(pixelmon['battleStats']['speed']))
	
	# moves
	if 'moves' in pixelmon:
		# leveling up moves
		pixelmonNew['levelUpMoves'] = pixelmon['moves']['levelUpMoves']
		# tutor moves
		pixelmonNew['tutorMoves'] = pixelmon['moves']['tutorMoves']
		# egg moves
		pixelmonNew['eggMoves'] = pixelmon['moves']['eggMoves']
		# tm 8 moves
		pixelmonNew['tmMoves8'] = pixelmon['moves']['tmMoves8']
		# tr moves
		pixelmonNew['trMoves'] = pixelmon['moves']['trMoves']
		# tranfer moves
		pixelmonNew['transferMoves'] = pixelmon['moves']['transferMoves']

def buildWikiStr(pixelmon, authors, moveset):
	wikiStr = """{{PokemonPrevNextHead
|type = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + """
|prevnum = 
|prev = 
|prevform = 
|nextnum = 
|next = 
|nextform = 
}}

{{Pokemon Infobox
|ndex = """ + pixelmon['ndex'] + """
|name = """ + pixelmon['name'] + """
|form = """ + pixelmon['form'] + """
|type1 = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + """
|gendercode = """ + pixelmon['gendercode'] + """
|growthrate = """ + pixelmon['growthrate'] + """
|expyield = """ + pixelmon['expyield'] + pixelmon['evYields'] + """
|catchrate = """ + pixelmon['catchrate'] + """
|friendship = """ + pixelmon['friendship'] + """
|ability1 = """ + pixelmon['ability1'] + (("""
|ability2 = """ + pixelmon['ability2']) if 'ability2' in pixelmon else ("")) + (("""
|hiddenability = """ + pixelmon['hiddenability']) if 'hiddenability' in pixelmon else ("")) + """
|egggroup1 = """ + pixelmon['egggroup1'] + (("""
|egggroup2 = """ + pixelmon['egggroup2']) if 'egggroup2' in pixelmon else ("")) + """
|eggsteps = """ + pixelmon['eggsteps'] + """
|height-m = """ + pixelmon['height-m'] + """
|weight-kg = """ + pixelmon['weight-kg'] + """
|species = """ + pixelmon['species'] + """}}

'''""" + pixelmon['form'] + " " + pixelmon['name'] + """''' is a """ + genPixelmonTypeDesc(pixelmon) + """ Pokémon introduced in Gen 8.


==Pokédex Entry==
{{DexEntry
|Some descriptions about this Pokémon in Pokédex.
|type1 = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + """}}

==Biology==
Some living habits and details about this Pokémon.

==Game locations==
{{Availability
|common =
|uncommon =
|rare =
|ultrarare =
|none = Users can customize the getting method themselves
|type1 = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + """}}

==Held Item==
{{HeldItems
|common =
|uncommon =
|rare =
|ultrarare =
|type1 = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + """}}

==Base Stats==
{{Stats
|type = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + pixelmon['Stats'] + """
}}

==Type Effectiveness==
{{TypeEffectiveness/header
|type = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + """
}}
{{TypeEffectiveness/entry
|type = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + genTypeEffect(pixelmon) + """
}}
|}

==Moves==
===By leveling up===
{{MoveLevelStart|""" + pixelmon['form'] + " " + pixelmon['name'] + "|" + pixelmon['type1'] + "|" + (pixelmon['type2'] if 'type2' in pixelmon else pixelmon['type1']) + """}}""" + genLevelUpMoveStr(pixelmon, moveset) + """
{{MoveLevelEnd|""" + pixelmon['form'] + " " + pixelmon['name'] + "|" + pixelmon['type1'] + "|" + (pixelmon['type2'] if 'type2' in pixelmon else pixelmon['type1']) + """}}

===By Gen 8 TM/TR===
{{MoveTM8Start|""" + pixelmon['form'] + " " + pixelmon['name'] + "|" + pixelmon['type1'] + "|" + (pixelmon['type2'] if 'type2' in pixelmon else pixelmon['type1']) + """}}""" + genTM8MoveStr(pixelmon, moveset) + genTRMoveStr(pixelmon, moveset) + """
{{MoveTM8End|""" + pixelmon['form'] + " " + pixelmon['name'] + "|" + pixelmon['type1'] + "|" + (pixelmon['type2'] if 'type2' in pixelmon else pixelmon['type1']) + """}}

===By breeding===
{{MoveBreedStart|""" + pixelmon['form'] + " " + pixelmon['name'] + "|" + pixelmon['type1'] + "|" + (pixelmon['type2'] if 'type2' in pixelmon else pixelmon['type1']) + """}}""" + genEggMoveStr(pixelmon, moveset) + """
{{MoveBreedEnd|""" + pixelmon['form'] + " " + pixelmon['name'] + "|" + pixelmon['type1'] + "|" + (pixelmon['type2'] if 'type2' in pixelmon else pixelmon['type1']) + """}}

===By tutoring===
{{MoveTutorStart|""" + pixelmon['form'] + " " + pixelmon['name'] + "|" + pixelmon['type1'] + "|" + (pixelmon['type2'] if 'type2' in pixelmon else pixelmon['type1']) + """}}""" + genTutorMoveStr(pixelmon, moveset) + genTransferMoveStr(pixelmon, moveset) + """
{{MoveTutorEnd|""" + pixelmon['form'] + " " + pixelmon['name'] + "|" + pixelmon['type1'] + "|" + (pixelmon['type2'] if 'type2' in pixelmon else pixelmon['type1']) + """}}

==Evolution==
{{Evobox-2
| type1   = 
| no1     = 
| name1   = 
| image1  = 
| type1-1 = 
| evo1    = 
| no2     = 
| name2   = 
| image2  = 
| type1-2 = 
}}

==Sprites==
{{Spritebox/Header
|type = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + """
}}
{{Spritebox/Image
|name = """ + pixelmon['name'] + """
|form = """ + pixelmon['form'] + """
}}
{{Spritebox/Footer|""" + pixelmon['ndex'] + """|""" + pixelmon['form'] + """}}

==Download Links==
{{DownloadLinks
|type1 = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + """
|cite = 
|data = 
|resource = 
}}

==Authors==
{{Author
|type1 = """ + pixelmon['type1'] + (("""
|type2 = """ + pixelmon['type2']) if 'type2' in pixelmon else ("")) + genAuthorStr(authors) + """
}}"""
	print(wikiStr)

def mapExpGroupName(oldName):
	newName = "Unknown"
	expGroupDict = {"Erratic": "Erratic",
		"Fast": "Fast",
		"Medium Fast": "Medium",
		"Medium Slow": "Parabolic",
		"Slow": "Slow",
		"Fluctuating": "Fluctuating"}
	if oldName in expGroupDict:
		newName = expGroupDict[oldName]
	return newName
	
def genAuthorStr(authors):
	authorStr = ""
	for i, val in enumerate(authors):
		if i == 0:
			authorStr += """
|data = """ + authors[0]
		elif i == 1:
			authorStr += """
|texture = """ + authors[1]
		elif i == 2:
			authorStr += """
|model = """ + authors[2]
	return authorStr
	
def isMoveStab(pixelmon, move, moveset):
	if move in moveset:
		if moveset[move]['attackType'] == pixelmon['type1'] and moveset[move]['attackCategory'] != 'Status' and moveset[move]['basePower'] > 0:
			return True
		elif 'type2' in pixelmon:
			if moveset[move]['attackType'] == pixelmon['type2'] and moveset[move]['attackCategory'] != 'Status' and moveset[move]['basePower'] > 0:
				return True
	return False
	
def genLevelUpMoveStr(pixelmon, moveset):
	moveStr = ""
	for moveElem in pixelmon['levelUpMoves']:
		for move in moveElem['attacks']:
			moveStr += """
{{MoveLevel+|""" + str(moveElem['level'] if moveElem['level'] != 0 else '') + "|" + move + ("|'''" if isMoveStab(pixelmon, move, moveset) else "") + """}}"""
	return moveStr
	
def genEggMoveStr(pixelmon, moveset):
	return genAbstractMoveStr(pixelmon, "eggMoves", "", moveset)
	
def genTM8MoveStr(pixelmon, moveset):
	return genAbstractMoveStr(pixelmon, "tmMoves8", "", moveset)

def genTRMoveStr(pixelmon, moveset):
	return genAbstractMoveStr(pixelmon, "trMoves", "", moveset)
	
def genTutorMoveStr(pixelmon, moveset):
	return genAbstractMoveStr(pixelmon, "tutorMoves", "Tutor", moveset)
	
def genTransferMoveStr(pixelmon, moveset):
	return genAbstractMoveStr(pixelmon, "transferMoves", "Transfer", moveset)

def genAbstractMoveStr(pixelmon, moveKey, moveType, moveset):
	moveStr = ""
	for move in pixelmon[moveKey]:
		moveStr += """
{{MoveLevel+|""" + moveType + "|" + move + ("|'''" if isMoveStab(pixelmon, move, moveset) else "") + """}}"""
	return moveStr

def genPixelmonTypeDesc(pixelmon):
	if 'type2' in pixelmon:
		typeStr = "dual-type {{Bt|" + pixelmon['type1'] + "}}/{{Bt|" + pixelmon['type2'] + "}}"
	else:
		typeStr = "{{Bt|" + pixelmon['type1'] + "}}-type"
	return typeStr

def genTypeEffect(pixelmon):
	typeDict = getTypeNum()
	str_TE = ""
	for i, val in enumerate(types):
		typeMultiplier = 1.0
		j = typeDict[pixelmon['type1']]
		typeMultiplier *= typeEffectList[i][j]
		if 'type2' in pixelmon:
			j2 = typeDict[pixelmon['type2']]
			typeMultiplier *= typeEffectList[i][j2]
		if typeMultiplier == 0:
			addStr = "0"
		elif typeMultiplier == 0.25:
			addStr = "1/4"
		elif typeMultiplier == 0.5:
			addStr = "1/2"
		elif typeMultiplier == 1.0:
			addStr = "1"
		elif typeMultiplier == 2.0:
			addStr = "2"
		elif typeMultiplier == 4.0:
			addStr = "4"
		else:
			addStr = "1"
		str_TE += """
|""" + val + " = " + addStr
	return str_TE
	
def cutAbilityName(ability):
	str_list = list(ability)
	i = 0
	while i < len(str_list):
		if str_list[i].isupper() and i > 0 and str_list[i-1] != '-':
			str_list.insert(i, ' ')
			i += 1
		i += 1
	return ''.join(str_list)

def cutEggGroupName(eggGroup):
	str_list = eggGroup.lower().split('_')
	str_res = str_list[0].capitalize()
	if len(str_list) > 1:
		str_part2 = str_list[1]
		if str_list[1] == 'one':
			str_part2 = '1'
		elif str_list[1] == 'two':
			str_part2 = '2'
		elif str_list[1] == 'three':
			str_part2 = '3'
		str_res += (" " + str_part2)
	return str_res

def cutAuthors(authorStr):
	# authors = ['Original Pixelmon data', 'Original Pixelmon Texture and Sprite', 'Original Pixelmon Model and Animation']
	authors = []
	if len(authorStr) == 0 or authorStr.isspace():
		return authors
	str_list = authorStr.split(',')
	if len(str_list) > 3:
		str_list = {str_list[0], str_list[1], str_list[2]}
	for i in enumerate(str_list):
		authors.append(i.strip())
	return authors
		
if __name__ == '__main__':
	jsonPath = input("Input your json file name, e.g. 226_mantine :")
	print("Input your author infos(data, texture and model author). Separate with comma, e.g. Blackout,wujichen158,NaGesei")
	authorStr = input("Leave blank to use the default authors:")
	authors = cutAuthors(authorStr)
	# authors = ["wujichen158", "wujichen158"]
	form = input("Input the Pokémon form you want to process to wiki format (Case sensitive!). Leave blank for Pokémon with no forms:")
	if len(form) == 0 or form.isspace():
		form = 'None'
	processData(readJSON(jsonPath+".json"), form, "", authors)
