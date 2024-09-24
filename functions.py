import os
import json
from datetime import datetime, date

ARMY_CONV = {
  "ESCLAVES":"E", "ESCLAVE":"E", "E":"E", 
  "MAÎTRESESCLAVES":"ME", "MAÎTREESCLAVE":"ME", "ME":"ME", 
  "JEUNESSOLDATES":"JS", "JEUNESOLDATE":"JS", "JS":"JS", 
  "SOLDATES":"S", "SOLDATE":"S", "S":"S", 
  "SOLDATESD'ÉLITE":"SE", "SOLDATED'ÉLITE":"SE", "SE":"SE", 
  "GARDIENNES":"G", "GARDIENNE":"G", "G":"G", 
  "GARDIENNESD'ÉLITE":"GE", "GARDIENNED'ÉLITE":"GE", "GE":"GE", 
  "TIRAILLEUSES":"T", "TIRAILLEUSE":"T", "T":"T", 
  "TIRAILLEUSESD'ÉLITE":"TE", "TIRAILLEUSED'ÉLITE":"TE", "TE":"TE", 
  "JEUNESLÉGIONNAIRES":"JL", "JEUNELÉGIONNAIRE":"JL", "JL":"JL", 
  "LÉGIONNAIRES":"L", "LÉGIONNAIRE":"L", "L":"L", 
  "LÉGIONNAIRESD'ÉLITE":"LE", "LÉGIONNAIRED'ÉLITE":"LE", "LE":"LE", 
  "JEUNESTANKS":"JTK", "JEUNETANK":"JTK", "JTK":"JTK", 
  "TANKS":"TK", "TANK":"TK", "TK":"TK", 
  "TANKSD'ÉLITE":"TKE", "TANKD'ÉLITE":"TKE", "TKE":"TKE"
}

NUMBERS = [str(i) for i in range(0,10)]


  

#__________________________________________________#
## GLOBAL VAR ##
#__________________________________________________#


S_JOUEUR_FILENAME = "STATS//Stats_Joueurs.json"

#__________________________________________________#
## CMD ##
#__________________________________________________#

def parseCMD(msgContent:str) -> str:
  res= msgContent.replace("  "," ")[:]
  keepFiltering= True
  while keepFiltering:
    if len(res.split(" \n"))>1:
      res= res.replace(" \n","\n")[:]
    else:
      keepFiltering= False
  keepFiltering= True
  while keepFiltering:
    if res[-1] == " ":
      res= res[:-1]
    else:
      keepFiltering= False
  return res



#__________________________________________________#
## DATA ##
#__________________________________________________#


def createArchive(filename):
  f = open(os.path.join(os.path.dirname(__file__), 'JSON//ARCHIVES//' + filename), 'w')
  f.close()
  

def loadData(filename):
  f = open(os.path.join(os.path.dirname(__file__), 'JSON//' + filename), 'r')
  d = json.load(f)
  f.close()
  return d


def saveData(data, filename):
  with open(os.path.join(os.path.dirname(__file__), 'JSON//' + filename),
            "w") as outfile:
    json.dump(data, outfile)



def dateMergeSort(arr):
  if len(arr) > 1:
    mid = len(arr) // 2
    left_half = dateMergeSort(arr[:mid])
    right_half = dateMergeSort(arr[mid:])
    res = arr[:]

    i = j = k = 0

    while i < len(left_half) and j < len(right_half):
        # Convert date strings to datetime objects for comparison
        if datetime.strptime(left_half[i], "%Y-%m-%d") < datetime.strptime(right_half[j], "%Y-%m-%d"):
          res[k] = left_half[i]
          i += 1
        else:
          res[k] = right_half[j]
          j += 1
        k += 1

    while i < len(left_half):
      res[k] = left_half[i]
      i += 1
      k += 1

    while j < len(right_half):
      res[k] = right_half[j]
      j += 1
      k += 1
    return res 
  else:
    return arr



def splitMessage(message) -> list:
  res = [""]
  lines = message.split("\n")
  triple_quote_open = False
  nbChar = 0
  pnt = 0
  
  for i in range(len(lines)) :
    nbCharLine = len(lines[i]) + 1
    if nbChar + nbCharLine > 2000 - 3:
      if triple_quote_open:
        res[pnt] += "```"
        res.append("```" + lines[i] + "\n")
        nbChar = nbCharLine + 3
      else:
        res.append(lines[i] + "\n")
        nbChar = nbCharLine
      pnt += 1
    else:
      if len(lines[i].split("```")) % 2 == 0 : 
        triple_quote_open = not triple_quote_open
      res[pnt] += lines[i] + "\n"
      nbChar += nbCharLine
  return res



def setCOLONIES() -> dict:
  data = loadData(S_JOUEUR_FILENAME)
  COLONIES = {}
  for p in data:
    COLONIES[p["name"].upper()] = [p["colo1"]["name"], p["colo2"]["name"]]
  return COLONIES


def log(rank= 0, prefixe= "", message= "", suffixe= ""):
  msg = ""
  filename = os.path.dirname(__file__)+"/LOGS/"+date.today().strftime("%Y-%m-%d")
  if not os.path.exists(filename):
    os.system("touch " + filename)
  for k in range(rank):
    msg+="\t"
  msg+= prefixe
  msg+= message
  msg+=suffixe
  os.system("echo "+msg+" >> "+ filename)


#__________________________________________________#
## NUMBERS ##
#__________________________________________________#


def convertNumber(number:str):
  count_last_zeros = 0
  for letter in number:
    if letter == "0":
      count_last_zeros += 1
    else:
      count_last_zeros = 0
  if count_last_zeros >= 9:
    number = number[:-9] + "G"
  elif count_last_zeros >= 6:
    number = number[:-6] + "M"
  elif count_last_zeros >= 3:
    number = number[:-3] + "k"
  return number

def readableNumber(number:str):
  L = len(number)
  res = ""
  for i in range(L):
    if i == L-1:
      res+= number[i]
    elif (L-i-1) % 3 == 0:
      res+= number[i]
      res+= "'"
    else:
      res+= number[i]
  return res

def betterNumber(number:str) -> str:
  if len(number) <= 3: return number
  elif number[-3:] == "000": return convertNumber(number)
  else: return readableNumber(number)

def getNumber(number:str) -> str:
  if "G" in number.upper():
    number = number.upper().replace("G", "000000000")
  elif "M" in number.upper():
    number = number.upper().replace("M", "000000")
  elif "K" in number.upper():
    number = number.upper().replace("K", "000")
  return number

def getArmy(army:str) -> dict:# 300 000 Esclaves, 10 Maîtres esclaves, 10 Jeunes soldates, 10 Soldates, 10 Soldates d'élite, 10 Gardiennes, 10 Gardiennes d'élite, 10 Tirailleuses, 10 Tirailleuses d'élite, 10 Jeunes légionnaires, 10 Légionnaires, 10 Légionnaires d'élite, 9 580 Jeunes tanks, 10 Tanks, 10 Tanks d'élite
  res = {}
  army = army.replace(" ", "")
  for unite in army.split(","):
    i = 0
    while i < len(unite) and unite[i] in NUMBERS:
      i+=1
    res[ARMY_CONV[unite[i:].upper()]] = int(unite[:i])
  return res