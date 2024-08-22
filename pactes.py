##v.1.0
#   Bloc-note
##

#__________________________________________________#
## import ##
#__________________________________________________#

import datetime
import functions as f

#__________________________________________________#
## GLOBAL VAR ##
#__________________________________________________#

H_PACTE_FILENAME = "HIST//Historique_Pactes.json"
H_FLOODS_FILENAME = "HIST//Historique_FloodsExternes.json"
S_TRANSACTIONS_FILENAME = "STATS//Stats_Transactions.json"
PACTES = f.loadData("CONST//CONST_Pactes.json")

#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#


def archiveFloods(ally, filename):
  msg = ""
  try:
    data = f.loadData(H_FLOODS_FILENAME)
    newData = []
    archivedData = []
  
    for flood in data:
      flooded = flood["flooded"]["ally"].upper()
      flooder = flood["flooder"]["ally"].upper()
      if flooded == ally.upper() or flooder == ally.upper(): 
        archivedData.append(flood)
      else:
        newData.append(flood)

    f.saveData(newData,H_FLOODS_FILENAME)
    f.saveData(archivedData,filename)
  except Exception as e:
    msg += "ERR: archiveFloods() - " + str(e) + "\n" + msg
  return msg


def printPactes() -> str:
  global PACTES
  data = f.loadData(H_PACTE_FILENAME)
  msg = """**Pactes**:\n```"""
  for p in data:
    end = p["end"] if p["end"] != "None" else "Pas de fin définie"
    msg+= "# "+ p["ally"] +  ":    "+ p["title"] + "\n"
    msg+= "    Début:  "+ str(p["start"]) + "\n"
    msg+= "    Fin:    " + end + "\n"
    msg+= "    Type de pacte guerrier:    " + PACTES["guerre"][int(p["type-guerre"])]["name"] + "\n"
    msg+= "    Type de pacte commercial:  " + PACTES["commerce"][int(p["type-commercial"])]["name"] + "\n"
    if int(p["type-commercial"]) == 0:
      pass
    elif int(p["type-commercial"]) == 1:
      msg+= "        Temps de location: " + str(p["n_days"]) + " jours\n"
    elif int(p["type-commercial"]) == 2:
      msg+= "        Prix pour 1M de TdC: " + f.convertNumber(str(p["price_for_1M_tdc"])) + " bois\n"
    elif int(p["type-commercial"]) == 3:
      msg+= "        Pourcentage de récupération: " + str(p["perc_flood"]) + "%\n"

    msg+= "\n" + p["description"] +"\n\n---------\n\n"
  msg+= "```"
  return msg


# 3 - `!endPacte <ally>`: clôt un pacte;
def endPacte(ally) -> str:
  msg = ""
  try:
    today = datetime.date.today().strftime("%Y-%m-%d")
    found = False
    data = f.loadData(H_PACTE_FILENAME)
    debut = ""
    for p in data:
      if p["ally"].upper() == ally.upper():
        found = True
        debut = p["start"]
        p["end"] = today
        f.saveData(data,H_PACTE_FILENAME)
        msg = "Pacte " + ally + " clôt."
        break
    if not found: 
      msg = "ERR: endPacte() - Aucun pacte trouvé pour cette alliance."
    else:
      f.createArchive(ally+"-"+debut+"-"+today+".json")

      archiveFloods(ally, "ARCHIVES//"+ally+"-"+debut+"-"+today+".json")
      
      transactions = f.loadData(S_TRANSACTIONS_FILENAME)
      if ally.upper() in transactions["achat-tdc"]:
        transactions["achat-tdc"][ally.upper()+"--"+today] = transactions["achat-tdc"][ally.upper()]
        transactions["achat-tdc"].pop(ally.upper(), None)
      if ally.upper() in transactions["location-tdc"]:
        transactions["location-tdc"][ally.upper()+"--"+today] = transactions["location-tdc"][ally.upper()]
        transactions["location-tdc"].pop(ally.upper(), None)
      if ally.upper() in transactions["perc-tdc"]:
        transactions["perc-tdc"][ally.upper()+"--"+today] = transactions["perc-tdc"][ally.upper()]
        transactions["perc-tdc"].pop(ally.upper(), None)
  except Exception as e:
    msg = "ERR: endPacte() - " + str(e) + "\n" + msg
  return "Pacte ajouté avec succès."


# 4 - `!pacte <ally> <type-guerre> <type-commerce> <sueilCommerce> <start> <end> \\n <titre> \\n <description>`: ajoute un nouveau pacte
def addPacte(message) -> str:
  msg = message.content.split("\n")
  ally = msg[0].split(" ")[1]

  if len(msg[0].split(" ")) == 6:
    msg[0] += " None"

  endPacte(ally)
  
  newData = {
    "ally": ally,
    "title": msg[1],
    "type-guerre": int(msg[0].split(" ")[2]),
    "type-commercial": int(msg[0].split(" ")[3]),
    "description": msg[2],
    "start": msg[0].split(" ")[5],
    "end": msg[0].split(" ")[6]
  }

  if int(msg[0].split(" ")[3]) == 0: pass
  elif int(msg[0].split(" ")[3]) == 1:
    newData["n_days"] = int(msg[0].split(" ")[4])
  elif int(msg[0].split(" ")[3]) == 2:
    newData["price_for_1M_tdc"] = int(f.getNumber(msg[0].split(" ")[4]))
  elif int(msg[0].split(" ")[3]) == 3:
    newData["perc_flood"] = int(msg[0].split(" ")[4])

  data = f.loadData(H_PACTE_FILENAME)
  data.append(newData)
  f.saveData(data, H_PACTE_FILENAME)

  data = f.loadData(S_TRANSACTIONS_FILENAME)
  if int(msg[0].split(" ")[3]) == 1:
    data["location-tdc"][ally.upper()] = {"tdc-pris": 0,"tdc-repris": 0}
  elif int(msg[0].split(" ")[3]) == 2:
    data["achat-tdc"][ally.upper()] = {"tdc-acheté": 0,"ressources-convoyées": 0}
  elif int(msg[0].split(" ")[3]) == 3:
    data["perc-tdc"][ally.upper()] = {"tdc-pris": 0,"tdc-repris": 0}
  f.saveData(data, S_TRANSACTIONS_FILENAME)
  return "Pacte ajouté avec succès."
