##v.1.0
#   Bloc-note
##

#__________________________________________________#
## import ##
#__________________________________________________#

import functions as f
import datetime

#__________________________________________________#
## GLOBAL VAR ##
#__________________________________________________#

H_FLOODS_FILENAME = "HIST//Historique_FloodsExternes.json"
H_PACTE_FILENAME = "HIST//Historique_Pactes.json"
H_CONVOIS_EXTERNES_FILENAME = "HIST//Historique_ConvoisExternes.json"
H_DONSTDC_FILENAME = "HIST//Historique_DonsTDC.json"
S_FLOODS_FILENAME = "STATS//Stats_FloodsFuturs.json"
PACTES = f.loadData("CONST//CONST_Pactes.json")

#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#

# fais le décompte des floods AllyEXT -> LF
def comptFloodsEXTtoLF(allyEXT:str):
  res = [0, 0]
  data = f.loadData(H_FLOODS_FILENAME)
  for flood in data:
    if flood["flooded"]["ally"].upper() == "LF" and flood["flooder"]["ally"].upper() == allyEXT.upper():
      res[0] += flood["quantity"]
    elif flood["flooder"]["ally"].upper() == "LF" and flood["flooded"]["ally"].upper() == allyEXT.upper():
      res[1] += flood["quantity"]
    else:
      pass
  return res # [ tdc pris par ext , tdc pris par LF ]


def comptTDCVenduToEXT(allyEXT:str, price_for_1M): # price = X tdc pour 1M de rss
  res = 0
  data = f.loadData(H_CONVOIS_EXTERNES_FILENAME)
  for convoi in data:
    print(convoi)
    if convoi["convoyed"]["ally"].upper() == "LF" and convoi["convoyer"]["ally"].upper() == allyEXT.upper():
      res += convoi["convoy"]["apple"] + convoi["convoy"]["wood"] + convoi["convoy"]["water"]
    else:
      pass
  return (res // 1000000) * price_for_1M


# !floodExtR [date:aaaa-mm-jj] [joueurLF] <joueurExtérieur> <ally> <quantité>
def floodExtR(date:str, playerLF:str, playerEXT:str, allyEXT:str, quantity:str)->str:
  error = saveFlood(playerLF, "LF", quantity, playerEXT, allyEXT, date)
  type = None
  data = f.loadData(H_PACTE_FILENAME)

  newDate = date
  newQuantity = quantity

  for p in data:
    if p["ally"].upper() == allyEXT.upper():
      print("ally found")
      type = p["type-commercial"]

      if type == 0:
        bilanTDC = comptFloodsEXTtoLF(allyEXT) # [ tdc pris par ext , tdc pris par LF ]
        decompteTDC = bilanTDC[0] - bilanTDC[1]
        newQuantity = min(decompteTDC, int(quantity))
        if newQuantity > 0:
          error = saveFloodFutur(date, str(newQuantity), allyEXT)

      elif type == 1: # location
        delay = int(p["n_days"])
        bilanTDC = comptFloodsEXTtoLF(allyEXT) # [ tdc pris par ext , tdc pris par LF ]
        decompteTDC = bilanTDC[0] - bilanTDC[1]
        newQuantity = min(decompteTDC, int(quantity))
        newDate = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days = delay)).strftime("%Y-%m-%d")
        if newQuantity > 0:
          error = saveFloodFutur(newDate, str(newQuantity), allyEXT)

      elif type == 2: # achat
        prix = int(p["price_for_1M_tdc"])
        bilanTDC = comptFloodsEXTtoLF(allyEXT) # [ tdc pris par ext , tdc pris par LF ]
        tdc_achete = comptTDCVenduToEXT(allyEXT, prix) # [ tdc vendu par ext ]
        decompteTDC = bilanTDC[0] - bilanTDC[1] - tdc_achete
        newQuantity = min(decompteTDC, int(quantity))
        if newQuantity > 0:
          error = saveFloodFutur(date, str(newQuantity), allyEXT)

      elif type == 3: # percentage_floods
        x = int(p["perc_flood"])
        bilanTDC = comptFloodsEXTtoLF(allyEXT) # [ tdc pris par ext , tdc pris par LF ]
        decompteTDC = (((100 - x) * bilanTDC[0]) / 100) // 1 - bilanTDC[1]
        newQuantity = min(decompteTDC, (((100 - x) * int(quantity)) / 100) // 1)
        if newQuantity > 0:
          error = saveFloodFutur(date, str(newQuantity), allyEXT)

  if type is None:
    bilanTDC = comptFloodsEXTtoLF(allyEXT) # [ tdc pris par ext , tdc pris par LF ]
    decompteTDC = bilanTDC[0] - bilanTDC[1]
    newQuantity = min(decompteTDC, int(quantity))
    if newQuantity > 0:
      error = saveFloodFutur(date, str(newQuantity), allyEXT)

  msg = playerEXT + " ["+allyEXT+"] a pris "+ f.betterNumber(str(quantity)) + "cm à "+ playerLF + "[LF].\n\n"
  msg += printFloodsFuturs()
  return msg

# !floodExtD [joueurLF] <joueurExtérieur> <ally> <quantité>
def floodExtD(date:str, playerLF:str, playerEXT:str, allyEXT:str, quantity:str)->str:
  error = saveFlood(playerEXT, allyEXT, quantity, playerLF, "LF", date)
  type = None
  data = f.loadData(S_FLOODS_FILENAME)
  q = int(quantity)
  indexToRemove = []
  
  for i in range(len(data)):
    print(q)
    if q == 0:
      pass
    else:
      if data[i]["ally"].upper() == allyEXT.upper():
        q2 = data[i]["quantity"]
        if q2 <= q:
          q -= q2
          indexToRemove.append(i)
        else:
          data[i]["quantity"] = data[i]["quantity"] - q
          q = 0
          print(data[i]["quantity"])

  print(indexToRemove)
  for i in range(len(indexToRemove)-1, -1, -1):
    data.pop(indexToRemove[i])

  f.saveData(data, S_FLOODS_FILENAME)

  msg =  playerLF + "[LF] a pris "+ f.betterNumber(quantity) + "cm à "+ playerEXT + " ["+allyEXT+"].\n\n"
  msg += printFloodsFuturs()
  return msg




def printFloodsExt() -> str:
  data = f.loadData(H_FLOODS_FILENAME)
  msg = "## Floods extérieurs:\n"
  MSG = ["",""]
  i = 0
  for flood in data:
    if flood["flooded"]["ally"].upper() == "LF": i = 0
    else: i = 1
    MSG[i] += "["+ flood["day"]+"] " + flood["flooder"]["player"]
    MSG[i] += "["+flood["flooder"]["ally"]+"] -> " + flood["flooded"]["player"]
    MSG[i] += "["+flood["flooded"]["ally"]+"]: "+f.convertNumber(str(flood["quantity"]))+ "\n"

  if MSG[0] == "": MSG[0] = "Aucun flood extérieur."
  if MSG[1] == "": MSG[1] = "Aucun flood extérieur."
  msg+= "### EXT -> LF:\n```" + MSG[0] + "```\n### LF -> EXT:\n```" + MSG[1] + "```\n"

  data = f.loadData(H_DONSTDC_FILENAME)
  msg += "## Dons de TDC:\n"
  MSG = ["",""]
  i = 0
  for don in data:
    if don["donnor"].upper() == "LF": i = 0
    else: i = 1
    MSG[i] += "["+ don["date"]+"] " + don["donnor"] +" -> " + don["receiver"] +": "+f.convertNumber(str(don["quantity"]))+ "\n"

  if MSG[0] == "": MSG[0] = "Aucun don extérieur."
  if MSG[1] == "": MSG[1] = "Aucun don extérieur."
  msg+= "### Don de la LF:\n```" + MSG[0] + "```\n### Don pour la LF:\n```" + MSG[1] + "```"
  
  return msg

def printFloodsExtAlly(ally:str) -> str:
  data = f.loadData(H_FLOODS_FILENAME)
  msg = "## Floods extérieurs:\n"
  MSG = ["",""]
  i = 0
  for flood in data:
    if flood["flooded"]["ally"].upper() == "LF" and flood["flooder"]["ally"].upper() == ally.upper(): 
      i = 0
    elif flood["flooder"]["ally"].upper() == "LF" and flood["flooded"]["ally"].upper() == ally.upper():
      i = 1
    MSG[i] += "["+ flood["day"]+"] " + flood["flooder"]["player"]
    MSG[i] += "["+flood["flooder"]["ally"]+"] -> " + flood["flooded"]["player"]
    MSG[i] += "["+flood["flooded"]["ally"]+"]: "+f.convertNumber(str(flood["quantity"]))+ "\n"

  if MSG[0] == "": MSG[0] = "Aucun flood extérieur."
  if MSG[1] == "": MSG[1] = "Aucun flood extérieur."
  msg+= "### "+ ally+" -> LF:\n```" + MSG[0] + "```\n### LF -> "+ ally+":\n```" + MSG[1] + "```\n"

  data = f.loadData(H_DONSTDC_FILENAME)
  msg += "## Dons de TDC:\n"
  MSG = ["",""]
  i = 0
  for don in data:
    if don["donnor"].upper() == "LF" and don["receiver"].upper() == ally.upper(): 
      i = 0
    elif don["receiver"].upper() == "LF" and don["donnor"].upper() == ally.upper(): 
      i = 1
    MSG[i] += "["+ don["date"]+"] " + don["donnor"] +" -> " + don["receiver"] +": "+f.convertNumber(str(don["quantity"]))+ "\n"

  if MSG[0] == "": MSG[0] = "Aucun don extérieur."
  if MSG[1] == "": MSG[1] = "Aucun don extérieur."
  msg+= "### Don de la LF:\n```" + MSG[0] + "```\n### Don pour la LF:\n```" + MSG[1] + "```"

  return msg



def printFloodsFuturs() -> str:
  data = f.loadData(S_FLOODS_FILENAME)
  floods = {}
  msg = ""

  for fl in data:
    if fl["date"] in floods: floods[fl["date"]].append([fl["quantity"], fl["ally"]])
    else: floods[fl["date"]] = [[fl["quantity"], fl["ally"]]]

  dates = []
  for k in floods.keys():
    dates.append(k)  
  sorted_dates = f.dateMergeSort(dates)

  msg = "## Floods en cours\n```"
  nf = 0
  state_date = 0
  for d in sorted_dates:
    if state_date == 0 and datetime.datetime.strptime(d, "%Y-%m-%d").date() > datetime.date.today():
      state_date = 1
      if msg[-1] == "`": msg+="Aucune récupération en cours."
      msg+= "```\n## Floods à venir\n```"
    msg_temp = {}
    qf = {}
    for fl in floods[d]:
      ally = str(fl[1])
      nf+=1
      if not ally in msg_temp: msg_temp[ally] = ""
      if not ally in qf: qf[ally] = 0
      qf[ally] += fl[0]
      msg_temp[ally]+= "- ["+d+"] " + str(fl[1]) + ": " + f.betterNumber(str(fl[0])) + " cm²\n"

    for ally in msg_temp:
      msg+= "["+d+"] " + ally + ": " + f.betterNumber(str(qf[ally])) + " cm² (Total)\n"
      msg+= msg_temp[ally]+"\n"

  if nf == 0: msg += "Aucun flood futur."
  msg+="```"
  return msg


def saveFlood(flooded:str, allyED:str, quantity:str, flooder:str, allyER:str, date:str)->str:
  error = ''
  data = f.loadData(H_FLOODS_FILENAME)
  flood = {
    "quantity": int(quantity),
    "flooded": {"ally": allyED, "player": flooded},
    "flooder": {"ally": allyER,"player": flooder},
    "day": date
  }
  data.append(flood)
  f.saveData(data,H_FLOODS_FILENAME)
  return error


def saveFloodFutur(date:str, quantity:str, allyEXT:str)->str:
  error = ''
  data = f.loadData(S_FLOODS_FILENAME)
  flood = {
    "date": date,
    "quantity": int(quantity),
    "ally": allyEXT
  }
  data.append(flood)
  f.saveData(data,S_FLOODS_FILENAME)
  return error


      
# 3 - `!donTDC <allianceDonneuse> <allianceReceveuse> <quantité> <raison>`: enregistre un don de tdc (butin de guerre par exemple)
def donTDC(allyD:str, allyR:str, quantity:str, reason:str) -> str:
  msg = ""
  try:
    data = f.loadData(H_DONSTDC_FILENAME)
    data.append({
      "donnor":allyD,
      "receiver":allyR,
      "quantity":int(quantity),
      "reason":reason,
      "date": datetime.date.today().strftime("%Y-%m-%d")
    })
    f.saveData(data, H_DONSTDC_FILENAME)
    msg = "Don enregistré avec succès."
  except Exception as e:
    msg = "ERR: donTDC() - " + str(e) + "\n" + msg
  return msg