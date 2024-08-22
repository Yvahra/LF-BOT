##v.1.0
#   Bloc-note
##

#__________________________________________________#
## import ##
#__________________________________________________#

import functions as f
from functions import convertNumber

#__________________________________________________#
## GLOBAL VAR ##
#__________________________________________________#

S_JOUEUR_FILENAME = "STATS//Stats_Joueurs.json"
RACES = ["Abeille", "Araignée", "Fourmi", "Termite"]
BONUS_HEROS = ["Vie", "FdF - Combat", "FdF - Chasse"]

#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#

def printPlayer(joueur:str) -> str:
  data = f.loadData(S_JOUEUR_FILENAME)
  msg = ""
  for i in range(len(data)):
    if data[i]["name"].upper() == joueur.upper():
      msg = "**"+ str(data[i]["name"]) + "**:\n```"
      if "race" in data[i]: msg += "    Race:       "+ RACES[data[i]["race"]]
      msg += "\n"
      msg += "    Mandibule:  " + str(data[i]["mandibule"]) + "\n"
      msg += "    Carapace:   " + str(data[i]["bouclier"]) + "\n"
      msg += "    Phéromones: " + str(data[i]["pheromones"])+ "\n"
      msg += "    Thermiques: " + str(data[i]["thermique"])+ "\n"
      msg += "--------------------\n"
      if "hero" in data[i]: 
        msg += "    Héros: +" + str(data[i]["hero"]["level"]) + "% (" + str(BONUS_HEROS[data[i]["hero"]["bonus"]]) +")\n"
      for colo in ["colo1", "colo2"]:
        if colo in data[i]: 
          msg += "--------------------\n"
          msg += "    Stats " + data[i][colo]["name"] + "\n"
          msg += "        Armées:\n"
          for unit in data[i][colo]["army"]:
            msg += "            " + unit.upper() + ": " + f.convertNumber(str(data[i][colo]["army"][unit]))+"\n"
          msg += "        Oe:           " + f.convertNumber(str(data[i][colo]["oe"]))+ "\n"
          msg += "        Ov:           " + f.convertNumber(str(data[i][colo]["ov"]))+ "\n"
          msg += "        TdC:          " + f.convertNumber(str(data[i][colo]["tdc"]))+ "\n"
          msg += "        TdC Exploité: " + f.convertNumber(str(data[i][colo]["exploitation"]))+ "\n"
          msg += "        TdP:          " + str(data[i][colo]["tdp"])+ "\n"
          if "vassal" in data[i][colo] and data[i][colo]["vassal"]["name"] != "":
            msg += "        Vassal: " + str(data[i][colo]["vassal"]["name"])+ "("
            if data[i][colo]["vassal"]["colony"] == 1: msg += "C1)"
            else: msg += "C2)"
            msg += "[" + str(data[i][colo]["vassal"]["pillage"]+20)+"%]\n"
  msg += "```"
  return msg

def addPlayer(message):
  newData = {
    "name": message.content.split("\n")[2].split(":")[1].split(",")[0].replace(" ", ""),
    "mandibule": int(message.content.split("\n")[3].split(":")[1].split(",")[0].replace(" ", "")),
    "bouclier": int(message.content.split("\n")[4].split(":")[1].split(",")[0].replace(" ", "")),
    "pheromones": int(message.content.split("\n")[5].split(":")[1].split(",")[0].replace(" ", "")),
    "race": int(message.content.split("\n")[6].split(":")[1].split(",")[0].replace(" ", "")),
    "thermique": int(message.content.split("\n")[7].split(":")[1].split(",")[0].replace(" ", "")),
    "hero":{
      "bonus": int(message.content.split("\n")[9].split(":")[1].split(",")[0].replace(" ", "")),
      "level": int(message.content.split("\n")[10].split(":")[1].split(",")[0].replace(" ", ""))
    },
    "colo1": {
      "name": message.content.split("\n")[13].split(":")[1].split(",")[0],
      "army": {

      },
      "oe": int(message.content.split("\n")[17].split(":")[1].split(",")[0].replace(" ", "")),
      "ov": int(message.content.split("\n")[18].split(":")[1].split(",")[0].replace(" ", "")),
      "tdc": int(message.content.split("\n")[19].split(":")[1].split(",")[0].replace(" ", "")),
      "exploitation": int(message.content.split("\n")[20].split(":")[1].split(",")[0].replace(" ", "")),
      "tdp": int(message.content.split("\n")[21].split(":")[1].split(",")[0].replace(" ", "")),
      "vassal": {
        "name": message.content.split("\n")[23].split(":")[1].split(",")[0].replace(" ", ""),
        "colony": int(message.content.split("\n")[24].split(":")[1].split(",")[0].replace(" ", "")),
        "pillage": int(message.content.split("\n")[25].split(":")[1].split(",")[0].replace(" ", ""))
      }
   },
    "colo2": {
      "name": message.content.split("\n")[29].split(":")[1].split(",")[0],
      "army": {

      },
      "oe": int(message.content.split("\n")[33].split(":")[1].split(",")[0].replace(" ", "")),
      "ov": int(message.content.split("\n")[34].split(":")[1].split(",")[0].replace(" ", "")),
      "tdc": int(message.content.split("\n")[35].split(":")[1].split(",")[0].replace(" ", "")),
      "exploitation": int(message.content.split("\n")[36].split(":")[1].split(",")[0].replace(" ", "")),
      "tdp": int(message.content.split("\n")[37].split(":")[1].split(",")[0].replace(" ", "")),
      "vassal": {
        "name": message.content.split("\n")[39].split(":")[1].split(",")[0].replace(" ", ""),
        "colony": int(message.content.split("\n")[40].split(":")[1].split(",")[0].replace(" ", "")),
        "pillage": int(message.content.split("\n")[41].split(":")[1].split(",")[0].replace(" ", ""))
      }
    }
  }

  for unite in message.content.split("\n")[15].split(","):
    newData["colo1"]["army"][unite.split(":")[0].replace(" ","").replace("\"","").lower()] = int(unite.split(":")[1].replace(" ",""))
  for unite in message.content.split("\n")[31].split(","):
    newData["colo2"]["army"][unite.split(":")[0].replace(" ","").replace("\"","").lower()] = int(unite.split(":")[1].replace(" ",""))

  data = f.loadData(S_JOUEUR_FILENAME)
  data.append(newData)
  f.saveData(data, S_JOUEUR_FILENAME)
  return "Joueur ajouté avec succès."



def setArmy(player:str, colo:str, army:str) -> str:
  msg = ""
  colo_name = ""
  try: 
    data = f.loadData(S_JOUEUR_FILENAME)
    for p in data:
      if p["name"].upper() == player.upper():
        colo = "colo1"if colo == "C1" else "colo2"
        p[colo]["army"] = f.getArmy(army)
        colo_name = p[colo]["name"]
    f.saveData(data, S_JOUEUR_FILENAME)
    msg = "Armée de la colonie " + colo_name + " de "+ player + " a été modifiée avec succès."
  except Exception as e:
    msg = "ERR: setArmy() - " + str(e) + "\n"+ msg
  return msg

def setRace(player:str, race:str) -> str:
  msg = ""
  try: 
    data = f.loadData(S_JOUEUR_FILENAME)
    for p in data:
      if p["name"].upper() == player.upper():
        p["race"] = int(race)
    f.saveData(data, S_JOUEUR_FILENAME)
    msg = "Race de "+ player + " modifiée avec succès."
  except Exception as e:
    msg = "ERR: setRace() - " + str(e) + "\n"+ msg
  return msg


def setStatsColo(player:str, colo:str, oe:str, ov:str, tdp:str) -> str:
  msg = ""
  colo_name = ""
  try: 
    data = f.loadData(S_JOUEUR_FILENAME)
    for p in data:
      if p["name"].upper() == player.upper():
        colo = "colo1"if colo == "C1" else "colo2"
        p[colo]["oe"] = int(oe)
        p[colo]["ov"] = int(ov)
        p[colo]["tdp"] = int(tdp)
        colo_name = p[colo]["name"]
    f.saveData(data, S_JOUEUR_FILENAME)
    msg = "Stats de la colonie " + colo_name + " de "+ player + " a été modifiée avec succès."
  except Exception as e:
    msg = "ERR: setStatsColo() - " + str(e) + "\n"+ msg
  return msg

def setVassal(player:str, colo:str, vassal:str, coloVassal:str, pillage:str) -> str:
  msg = ""
  colo_name = ""
  try: 
    data = f.loadData(S_JOUEUR_FILENAME)
    for p in data:
      if p["name"].upper() == player.upper():
        colo = "colo1"if colo == "C1" else "colo2"
        p[colo]["vassal"]["name"] = vassal
        p[colo]["vassal"]["colony"] = 1 if coloVassal == "C2" else 0
        p[colo]["vassal"]["pillage"] = int(pillage)
    f.saveData(data, S_JOUEUR_FILENAME)
    colo_name = p[colo]["name"]
    msg = "Vassal de la colo " + colo_name + " de "+ player + " a été modifié avec succès."
  except Exception as e:
    msg = "ERR: setVassal() - " + str(e) + "\n"+ msg
  return msg

def setStatsPlayer(player:str, mandi:str, cara:str, phero: str, therm:str) -> str:
  msg = ""
  try: 
    data = f.loadData(S_JOUEUR_FILENAME)
    for p in data:
      if p["name"].upper() == player.upper():
        p["mandibule"] = int(mandi)
        p["carapace"] = int(cara)
        p["pheromones"] = int(phero)
        p["thermique"] = int(therm)
    f.saveData(data, S_JOUEUR_FILENAME)
    msg = "Stats générales de "+ player + " modifiées avec succès."
  except Exception as e:
    msg = "ERR: setStatsPlayer() - " + str(e) + "\n"+ msg
  return msg

def setHero(player:str, bonus:str, level:str) -> str:
  msg = ""
  try: 
    data = f.loadData(S_JOUEUR_FILENAME)
    for p in data:
      if p["name"].upper() == player.upper():
        p["hero"]["bonus"] = int(bonus)
        p["hero"]["level"] = int(level)
    f.saveData(data, S_JOUEUR_FILENAME)
    msg = "Héros de "+ player + " modifié avec succès."
  except Exception as e:
    msg = "ERR: setHero() - " + str(e) + "\n"+ msg
  return msg


def setTDCExploité(player:str, colo:str, tdc:str) -> str:
  msg = ""
  try:
    data = f.loadData(S_JOUEUR_FILENAME)
    old_tdc = ""
    for p in data:
      if p["name"].upper() == player.upper():
        colo_key = "colo1" if colo.upper() == "C1" else "colo2"
        if "exploitation" in p[colo_key]:
          old_tdc = str(p[colo_key]["exploitation"])
        p[colo_key]["exploitation"] = int(tdc)
        if int(tdc) > p[colo_key]["tdc"]:
          p[colo_key]["tdc"] = int(tdc)
    f.saveData(data, S_JOUEUR_FILENAME)
    msg = "TdC exploité de " + player + "("+colo+") modifiées avec succès. [" + f.convertNumber(old_tdc) + ">"+f.convertNumber(tdc) + "]"
  except Exception as e:
    msg = "ERR: setTDCExploité() - " + str(e) + "\n" + msg
  return msg


def setTDC(player, colo:str, tdc:str) -> str:
  msg = ""
  try:
    data = f.loadData(S_JOUEUR_FILENAME)
    old_tdc = ""
    for p in data:
      if p["name"].upper() == player.upper():
        colo_key = "colo1" if colo.upper() == "C1" else "colo2"
        if "tdc" in p[colo_key]: old_tdc = str(p[colo_key]["tdc"])
        p[colo_key]["tdc"] = int(tdc)
        if int(tdc) < p[colo_key]["exploitation"]: p[colo_key]["exploitation"] = int(tdc)
    f.saveData(data, S_JOUEUR_FILENAME)
    msg = "TdC de " + player + "("+colo+") modifiées avec succès. [" + f.convertNumber(old_tdc) + ">"+f.convertNumber(tdc) + "]"
  except Exception as e:
    msg = "ERR: setTDC() - " + str(e) + "\n" + msg
  return msg
