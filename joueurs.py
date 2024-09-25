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
S_ALLIE_FILENAME = "STATS//Stats_Allies.json"
S_ACTIVE_PLAYERS = "STATS//Stats_JoueursActifs.json"
S_ALLIANCE_FILENAME = "STATS//Stats_Alliance.json"
RACES = ["Abeille", "Araignée", "Fourmi", "Termite"]
BONUS_HEROS = ["Vie", "FdF - Combat", "FdF - Chasse"]
DATA_ARMY = {
  "OV":{"tdp":60, "vie":0,"fdf":0, "fdd":0},
  "E":{"tdp":336, "vie":4,"fdf":4, "fdd":3},
  "ME":{"tdp":504, "vie":6,"fdf":6, "fdd":4},
  "JS":{"tdp":588, "vie":16,"fdf":8, "fdd":7},
  "S":{"tdp":756, "vie":20,"fdf":11, "fdd":10},
  "SE":{"tdp":1008, "vie":26,"fdf":17, "fdd":14},
  "G":{"tdp":1008, "vie":25,"fdf":1, "fdd":27},
  "GE":{"tdp":1344, "vie":32,"fdf":1, "fdd":35},
  "T":{"tdp":1176, "vie":12,"fdf":32, "fdd":10},
  "TE":{"tdp":1512, "vie":15,"fdf":40, "fdd":12},
  "JL":{"tdp":1848, "vie":40,"fdf":45, "fdd":35},
  "L":{"tdp":2520, "vie":55,"fdf":60, "fdd":45},
  "LE":{"tdp":2940, "vie":60,"fdf":65, "fdd":50},
  "JTK":{"tdp":3024, "vie":40,"fdf":80, "fdd":1},
  "TK":{"tdp":5712, "vie":70,"fdf":140, "fdd":1},
  "TKE":{"tdp":6974, "vie":80,"fdf":160, "fdd":1}
}

#__________________________________________________#
## OBJECT ##
#__________________________________________________#

class Joueur:
  def __init__(self, name):
    self.name=        name
    self.valide=      False
    self.race=        None
    self.mandibule=   None
    self.carapace=    None
    self.pheromones=  None
    self.thermique=   None
    self.hero=        { "bonus": None, "level": None}
    self.colo1 =      None
    self.colo2 =      None

    for file in [S_JOUEUR_FILENAME,S_ALLIE_FILENAME]:
      data = f.loadData(file)
      for i in range(len(data)):
        if data[i]["name"].upper() == name.upper():
          self.valide= True
          if "race" in data[i]:       self.race=        int(data[i]["race"])
          if "mandibule" in data[i]:  self.mandibule=   int(data[i]["mandibule"])
          if "bouclier" in data[i]:   self.carapace=    int(data[i]["bouclier"])
          if "pheromones" in data[i]: self.pheromones=  int(data[i]["pheromones"])
          if "thermique" in data[i]:  self.thermique=   int(data[i]["thermique"])
          if "hero" in data[i]:
            self.hero= {
              "bonus": int(data[i]["hero"]["bonus"]),
              "level": int(data[i]["hero"]["level"])
            }
          for colo in ["colo1", "colo2"]:
            if colo in data[i]:
              temp = dict()
              temp["name"]= str(data[i][colo]["name"])
              temp["army"]= {}
              fdf_hb = 0
              vie_hb = 0
              fdd_hb = 0
              tdp_hb = 0
              for unit in data[i][colo]["army"]:
                temp["army"][unit.upper()]= int(data[i][colo]["army"][unit])
                fdf_hb += data[i][colo]["army"][unit] * DATA_ARMY[unit.upper()]["fdf"]
                vie_hb += data[i][colo]["army"][unit] * DATA_ARMY[unit.upper()]["vie"]
                fdd_hb += data[i][colo]["army"][unit] * DATA_ARMY[unit.upper()]["fdd"]
                tdp_hb += data[i][colo]["army"][unit] * DATA_ARMY[unit.upper()]["tdp"]
              temp["stats_army"] =  {"fdf_hb":fdf_hb,"vie_hb":vie_hb,"fdd_hb":fdd_hb,"tdp_hb":tdp_hb}
              temp["oe"]=           int(data[i][colo]["oe"])
              temp["ov"]=           int(data[i][colo]["ov"])
              temp["tdc"]=          int(data[i][colo]["tdc"])
              temp["tdc_exploit"]=  int(data[i][colo]["exploitation"])
              temp["tdp"]=          int(data[i][colo]["tdp"])
              if "vassal" in data[i][colo] and data[i][colo]["vassal"]["name"] != "":
                temp["vassal"]=             dict()
                temp["vassal"]["name"]=     str(data[i][colo]["vassal"]["name"])
                temp["vassal"]["colo"]=     int(data[i][colo]["vassal"]["colony"])
                temp["vassal"]["pillage"]=  int(data[i][colo]["vassal"]["pillage"])
              if colo == "colo1":
                self.colo1 = temp
              else:
                self.colo2 = temp

  def isValide(self):
    return self.valide

  def optiMandi(self) -> str:
    msg= self.name + " n'est pas un joueur valide pour calculer sa rentabilité de mandibule."
    data = f.loadData(S_ALLIANCE_FILENAME)
    bonus_ally_tdp = int(data["bonus"]["tdp"])
    if self.isValide():
      cout=   int(50.0*(1.7**(self.mandibule+1)))
      msg=    "```Coût ouvrières:         " + f.betterNumber(str(cout))
      tdp_ov= round(cout*(DATA_ARMY["OV"]["tdp"]*(0.95**self.colo1["tdp"])*(0.99**bonus_ally_tdp) / (24*3600)),2)
      msg+=   " (" + str(tdp_ov) + "j)\n"

      fdf_hb= self.colo1["stats_army"]["fdf_hb"]
      if self.colo2 != None:
        fdf_hb+= self.colo2["stats_army"]["fdf_hb"]
      bonus= 0
      if not self.hero is None:
        bonus= 0 if self.hero["bonus"] == 0 else self.hero["level"]
      fdf=    fdf_hb*(1+self.mandibule*0.05+bonus/100)
      fdfp1=  fdf_hb*(1+(self.mandibule+1)*0.05+bonus/100)
      d_fdf=  fdfp1 - fdf
      msg+=   "FdF gagnée:             "+f.betterNumber(str(int(d_fdf))) + "\n"

      nb_jtk= d_fdf / (DATA_ARMY["JTK"]["fdf"] * (1+self.mandibule * 0.05+ bonus / 100))
      msg+=   "Nb de JTk équivalentes: " + f.betterNumber(str(int(nb_jtk)))
      tdp_jtk = round(nb_jtk * (DATA_ARMY["JTK"]["tdp"] * (0.95 ** self.colo1["tdp"]) * (0.99 ** bonus_ally_tdp) / (24 * 3600)), 2)
      msg += " (" + str(tdp_jtk) + "j)\n"

      msg += "```\nIl vaut mieux **"
      if tdp_ov < tdp_jtk:
        msg+= "augmenter les mandibules!**"
      else:
        msg+= "pondre des Jeunes Tanks!**"
      return msg

  def optiCara(self) -> str:
    msg= self.name + " n'est pas un joueur valide pour calculer sa rentabilité de carapace."
    data = f.loadData(S_ALLIANCE_FILENAME)
    bonus_ally_tdp = int(data["bonus"]["tdp"])
    bonus_ally_vie = int(data["bonus"]["health"])
    if self.isValide():
      cout=   int(50.0*(1.7**(self.carapace+1)))
      msg=    "```Coût ouvrières:         " + f.betterNumber(str(cout))
      tdp_ov= round(cout*(DATA_ARMY["OV"]["tdp"]*(0.95**self.colo1["tdp"])*(0.99**bonus_ally_tdp) / (24*3600)),2)
      msg+=   " (" + str(tdp_ov) + "j)\n"

      vie_hb= self.colo1["stats_army"]["vie_hb"]
      if self.colo2 != None:
        vie_hb+= self.colo2["stats_army"]["vie_hb"]
      bonus= 0
      if not self.hero is None:
        bonus= 0 if self.hero["bonus"] != 0 else self.hero["level"]
      vie=    vie_hb*(1+self.carapace*0.05 + bonus_ally_vie/100 + bonus/100)
      viep1=  vie_hb*(1+(self.carapace+1)*0.05 + bonus_ally_vie/100 + bonus/100)
      d_vie=  viep1 - vie
      msg+=   "Vie gagnée:             "+f.betterNumber(str(int(d_vie))) + "\n"

      nb_js=  d_vie / (DATA_ARMY["JS"]["vie"] * (1+self.carapace * 0.05+ bonus_ally_vie/100 + bonus/100))
      msg+=   "Nb de JS équivalentes:  " + f.betterNumber(str(int(nb_js)))
      tdp_js= round(nb_js * (DATA_ARMY["JS"]["vie"] * (0.95 ** self.colo1["tdp"]) * (0.99 ** bonus_ally_tdp) / (24 * 3600)), 2)
      msg +=  " (" + str(tdp_js) + "j)\n"

      msg += "```\nIl vaut mieux **"
      if tdp_ov < tdp_js:
        msg+= "augmenter la carapace!**"
      else:
        msg+= "pondre des Jeunes Soldates!**"
      return msg

#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#

def printPlayer(joueur:str) -> str:
  msg = "ERR: Pas de joueur nommé \""+joueur+"\""
  for file in [S_JOUEUR_FILENAME, S_ALLIE_FILENAME]:
    data = f.loadData(file)
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

def addPlayer(command):
  newData = {
    "name": command.split("\n")[2].split(":")[1].split(",")[0].replace(" ", ""),
    "mandibule": int(command.split("\n")[3].split(":")[1].split(",")[0].replace(" ", "")),
    "bouclier": int(command.split("\n")[4].split(":")[1].split(",")[0].replace(" ", "")),
    "pheromones": int(command.split("\n")[5].split(":")[1].split(",")[0].replace(" ", "")),
    "race": int(command.split("\n")[6].split(":")[1].split(",")[0].replace(" ", "")),
    "thermique": int(command.split("\n")[7].split(":")[1].split(",")[0].replace(" ", "")),
    "hero":{
      "bonus": int(command.split("\n")[9].split(":")[1].split(",")[0].replace(" ", "")),
      "level": int(command.split("\n")[10].split(":")[1].split(",")[0].replace(" ", ""))
    },
    "colo1": {
      "name": command.split("\n")[13].split(":")[1].split(",")[0],
      "army": {

      },
      "oe": int(command.split("\n")[17].split(":")[1].split(",")[0].replace(" ", "")),
      "ov": int(command.split("\n")[18].split(":")[1].split(",")[0].replace(" ", "")),
      "tdc": int(command.split("\n")[19].split(":")[1].split(",")[0].replace(" ", "")),
      "exploitation": int(command.split("\n")[20].split(":")[1].split(",")[0].replace(" ", "")),
      "tdp": int(command.split("\n")[21].split(":")[1].split(",")[0].replace(" ", "")),
      "vassal": {
        "name": command.split("\n")[23].split(":")[1].split(",")[0].replace(" ", ""),
        "colony": int(command.split("\n")[24].split(":")[1].split(",")[0].replace(" ", "")),
        "pillage": int(command.split("\n")[25].split(":")[1].split(",")[0].replace(" ", ""))
      }
   },
    "colo2": {
      "name": command.split("\n")[29].split(":")[1].split(",")[0],
      "army": {

      },
      "oe": int(command.split("\n")[33].split(":")[1].split(",")[0].replace(" ", "")),
      "ov": int(command.split("\n")[34].split(":")[1].split(",")[0].replace(" ", "")),
      "tdc": int(command.split("\n")[35].split(":")[1].split(",")[0].replace(" ", "")),
      "exploitation": int(command.split("\n")[36].split(":")[1].split(",")[0].replace(" ", "")),
      "tdp": int(command.split("\n")[37].split(":")[1].split(",")[0].replace(" ", "")),
      "vassal": {
        "name": command.split("\n")[39].split(":")[1].split(",")[0].replace(" ", ""),
        "colony": int(command.split("\n")[40].split(":")[1].split(",")[0].replace(" ", "")),
        "pillage": int(command.split("\n")[41].split(":")[1].split(",")[0].replace(" ", ""))
      }
    }
  }

  for unite in command.split("\n")[15].split(","):
    newData["colo1"]["army"][unite.split(":")[0].replace(" ","").replace("\"","").lower()] = int(unite.split(":")[1].replace(" ",""))
  for unite in command.split("\n")[31].split(","):
    newData["colo2"]["army"][unite.split(":")[0].replace(" ","").replace("\"","").lower()] = int(unite.split(":")[1].replace(" ",""))

  data = f.loadData(S_JOUEUR_FILENAME)
  data.append(newData)
  f.saveData(data, S_JOUEUR_FILENAME)
  return "Joueur ajouté avec succès."

def addAllie(command):
  newData = {
    "name": command.split("\n")[2].split(":")[1].split(",")[0].replace(" ", ""),
    "mandibule": int(command.split("\n")[3].split(":")[1].split(",")[0].replace(" ", "")),
    "bouclier": int(command.split("\n")[4].split(":")[1].split(",")[0].replace(" ", "")),
    "pheromones": int(command.split("\n")[5].split(":")[1].split(",")[0].replace(" ", "")),
    "race": int(command.split("\n")[6].split(":")[1].split(",")[0].replace(" ", "")),
    "thermique": int(command.split("\n")[7].split(":")[1].split(",")[0].replace(" ", "")),
    "hero":{
      "bonus": int(command.split("\n")[9].split(":")[1].split(",")[0].replace(" ", "")),
      "level": int(command.split("\n")[10].split(":")[1].split(",")[0].replace(" ", ""))
    },
    "colo1": {
      "name": command.split("\n")[13].split(":")[1].split(",")[0],
      "army": {

      },
      "oe": int(command.split("\n")[17].split(":")[1].split(",")[0].replace(" ", "")),
      "ov": int(command.split("\n")[18].split(":")[1].split(",")[0].replace(" ", "")),
      "tdc": int(command.split("\n")[19].split(":")[1].split(",")[0].replace(" ", "")),
      "exploitation": int(command.split("\n")[20].split(":")[1].split(",")[0].replace(" ", "")),
      "tdp": int(command.split("\n")[21].split(":")[1].split(",")[0].replace(" ", "")),
      "vassal": {
        "name": command.split("\n")[23].split(":")[1].split(",")[0].replace(" ", ""),
        "colony": int(command.split("\n")[24].split(":")[1].split(",")[0].replace(" ", "")),
        "pillage": int(command.split("\n")[25].split(":")[1].split(",")[0].replace(" ", ""))
      }
   },
    "colo2": {
      "name": command.split("\n")[29].split(":")[1].split(",")[0],
      "army": {

      },
      "oe": int(command.split("\n")[33].split(":")[1].split(",")[0].replace(" ", "")),
      "ov": int(command.split("\n")[34].split(":")[1].split(",")[0].replace(" ", "")),
      "tdc": int(command.split("\n")[35].split(":")[1].split(",")[0].replace(" ", "")),
      "exploitation": int(command.split("\n")[36].split(":")[1].split(",")[0].replace(" ", "")),
      "tdp": int(command.split("\n")[37].split(":")[1].split(",")[0].replace(" ", "")),
      "vassal": {
        "name": command.split("\n")[39].split(":")[1].split(",")[0].replace(" ", ""),
        "colony": int(command.split("\n")[40].split(":")[1].split(",")[0].replace(" ", "")),
        "pillage": int(command.split("\n")[41].split(":")[1].split(",")[0].replace(" ", ""))
      }
    }
  }

  for unite in command.split("\n")[15].split(","):
    newData["colo1"]["army"][unite.split(":")[0].replace(" ","").replace("\"","").lower()] = int(unite.split(":")[1].replace(" ",""))
  for unite in command.split("\n")[31].split(","):
    newData["colo2"]["army"][unite.split(":")[0].replace(" ","").replace("\"","").lower()] = int(unite.split(":")[1].replace(" ",""))

  data = f.loadData(S_ALLIE_FILENAME)
  data.append(newData)
  f.saveData(data, S_ALLIE_FILENAME)
  return "Joueur ajouté avec succès."

def renameColo(player:str, colo:str, name:str) -> str:
  msg = "ERR: Pas de joueur nommé \""+player+"\""
  old_colo_name = ""
  try:
    for file in [S_JOUEUR_FILENAME, S_ALLIE_FILENAME]:
      found= False
      data = f.loadData(file)
      for p in data:
        if p["name"].upper() == player.upper():
          found= True
          colo = "colo1" if colo.upper() == "C1" else "colo2"
          old_colo_name = p[colo]["name"]
          p[colo]["name"] = name
      if found:
        f.saveData(data, file)
        msg = "Nom de la colonie de "+ player + " a été modifiée avec succès. [" + old_colo_name + " > " + name + "]"
  except Exception as e:
    msg = "ERR: renameColo() - " + str(e) + "\n"+ msg
  return msg

def setArmy(player:str, colo:str, army:str) -> str:
  msg = "ERR: Pas de joueur nommé \""+player+"\""
  colo_name = ""
  try: 
    for file in [S_JOUEUR_FILENAME,S_ALLIE_FILENAME]:
      data = f.loadData(file)
      found= False
      for p in data:
        if p["name"].upper() == player.upper():
          found= True
          colo = "colo1" if colo.upper() == "C1" else "colo2"
          p[colo]["army"] = f.getArmy(army)
          colo_name = p[colo]["name"]
      if found:
        f.saveData(data, file)
        msg = "Armée de la colonie " + colo_name + " de "+ player + " a été modifiée avec succès."
  except Exception as e:
    msg = "ERR: setArmy() - " + str(e) + "\n"+ msg
  return msg

def setRace(player:str, race:str) -> str:
  msg = "ERR: Pas de joueur nommé \""+player+"\""
  try:
    for file in [S_JOUEUR_FILENAME, S_ALLIE_FILENAME]:
      data = f.loadData(file)
      found= False
      for p in data:
        if p["name"].upper() == player.upper():
          found= True
          p["race"] = int(race)
      if found:
        f.saveData(data, file)
        msg = "Race de "+ player + " modifiée avec succès."
  except Exception as e:
    msg = "ERR: setRace() - " + str(e) + "\n"+ msg
  return msg


def setStatsColo(player:str, colo:str, oe:str, ov:str, tdp:str) -> str:
  msg = "ERR: Pas de joueur nommé \""+player+"\""
  colo_name = ""
  try:
    for file in [S_JOUEUR_FILENAME, S_ALLIE_FILENAME]:
      data = f.loadData(file)
      found= False
      for p in data:
        if p["name"].upper() == player.upper():
          found= True
          colo = "colo1" if colo.upper() == "C1" else "colo2"
          p[colo]["oe"] = int(oe)
          p[colo]["ov"] = int(ov)
          p[colo]["tdp"] = int(tdp)
          colo_name = p[colo]["name"]
      if found:
        f.saveData(data, file)
        msg = "Stats de la colonie " + colo_name + " de "+ player + " a été modifiée avec succès."
  except Exception as e:
    msg = "ERR: setStatsColo() - " + str(e) + "\n"+ msg
  return msg

def setVassal(player:str, colo:str, vassal:str, coloVassal:str, pillage:str) -> str:
  msg = "ERR: Pas de joueur nommé \""+player+"\""
  colo_name = ""
  try: 
    for file in [S_JOUEUR_FILENAME,S_ALLIE_FILENAME]:
      data = f.loadData(file)
      found= False
      colo_name= ""
      for p in data:
        if p["name"].upper() == player.upper():
          found= True
          colo = "colo1" if colo.upper() == "C1" else "colo2"
          p[colo]["vassal"]["name"] = vassal
          p[colo]["vassal"]["colony"] = 1 if coloVassal == "C2" else 0
          p[colo]["vassal"]["pillage"] = int(pillage)
          colo_name = p[colo]["name"]
      if found:
        f.saveData(data, file)
        msg = "Vassal de la colo " + colo_name + " de "+ player + " a été modifié avec succès."
  except Exception as e:
    msg = "ERR: setVassal() - " + str(e) + "\n"+ msg
  return msg

def setStatsPlayer(player:str, mandi:str, cara:str, phero: str, therm:str) -> str:
  msg = "ERR: Pas de joueur nommé \""+player+"\""
  try:
    for file in [S_JOUEUR_FILENAME, S_ALLIE_FILENAME]:
      data = f.loadData(file)
      found= False
      for p in data:
        if p["name"].upper() == player.upper():
          found= True
          p["mandibule"] = int(mandi)
          p["carapace"] = int(cara)
          p["pheromones"] = int(phero)
          p["thermique"] = int(therm)
      if found:
        f.saveData(data, file)
        msg = "Stats générales de "+ player + " modifiées avec succès."
  except Exception as e:
    msg = "ERR: setStatsPlayer() - " + str(e) + "\n"+ msg
  return msg

def setHero(player:str, bonus:str, level:str) -> str:
  msg = "ERR: Pas de joueur nommé \""+player+"\""
  try:
    for file in [S_JOUEUR_FILENAME, S_ALLIE_FILENAME]:
      data = f.loadData(file)
      found= False
      for p in data:
        if p["name"].upper() == player.upper():
          found= True
          p["hero"]["bonus"] = int(bonus)
          p["hero"]["level"] = int(level)
      if found:
        f.saveData(data, file)
        msg = "Héros de "+ player + " modifié avec succès."
  except Exception as e:
    msg = "ERR: setHero() - " + str(e) + "\n"+ msg
  return msg


def setTDCExploité(player:str, colo:str, tdc:str) -> str:
  msg = "ERR: Pas de joueur nommé \""+player+"\""
  try:
    for file in [S_JOUEUR_FILENAME, S_ALLIE_FILENAME]:
      data = f.loadData(file)
      old_tdc = ""
      found= False
      for p in data:
        if p["name"].upper() == player.upper():
          found= True
          colo_key = "colo1" if colo.upper() == "C1" else "colo2"
          if "exploitation" in p[colo_key]:
            old_tdc = str(p[colo_key]["exploitation"])
          p[colo_key]["exploitation"] = int(tdc)
          if int(tdc) > p[colo_key]["tdc"]:
            p[colo_key]["tdc"] = int(tdc)
      if found:
        f.saveData(data, file)
        msg = "TdC exploité de " + player + "("+colo+") modifiées avec succès. [" + f.convertNumber(old_tdc) + ">"+f.convertNumber(tdc) + "]"
  except Exception as e:
    msg = "ERR: setTDCExploité() - " + str(e) + "\n" + msg
  return msg


def getTDCExploités() -> str:
  msg = "ERR:"
  try:
    activePlayers= f.loadData(S_ACTIVE_PLAYERS)
    data = f.loadData(S_JOUEUR_FILENAME)
    old_tdc = ""
    found= False
    msg= "## Exploitations de tdc"
    joueursManquants= []
    for activePlayer in activePlayers:
      found= False
      for p in data:
        if p["name"].upper() == activePlayer.upper():
          found= False
          msg+= "\n" + p["name"]
          msg+= ": "
          msg+= f.betterNumber(str(p["colo1"]["exploitation"])) + "(" + p["colo1"]["name"] + ")"
          if "colo2" in p:
            msg += ", " + f.betterNumber(str(p["colo2"]["exploitation"])) + "(" + p["colo2"]["name"] + ")"
      if not found:
        joueursManquants.append(activePlayer)
    if len(joueursManquants)>0:
      msg+="\n## Joueurs manquants"
      for j in joueursManquants:
        msg+="\n"+j
  except Exception as e:
    msg = "ERR: getTDCExploités() - " + str(e) + "\n" + msg
  return msg



def setTDC(player:str, colo:str, tdc:str) -> str:
  msg = "ERR: Pas de joueur nommé \""+player+"\""
  try:
    for file in [S_JOUEUR_FILENAME, S_ALLIE_FILENAME]:
      data = f.loadData(file)
      old_tdc = ""
      found= False
      for p in data:
        if p["name"].upper() == player.upper():
          found= True
          colo_key = "colo1" if colo.upper() == "C1" else "colo2"
          if "tdc" in p[colo_key]: old_tdc = str(p[colo_key]["tdc"])
          p[colo_key]["tdc"] = int(tdc)
          if int(tdc) < p[colo_key]["exploitation"]: p[colo_key]["exploitation"] = int(tdc)
      if found:
        f.saveData(data, file)
        msg = "TdC de " + player + "("+colo+") modifiées avec succès. [" + f.convertNumber(old_tdc) + ">"+f.convertNumber(tdc) + "]"
  except Exception as e:
    msg = "ERR: setTDC() - " + str(e) + "\n" + msg
  return msg

def setActivePlayers(command):
  res = []
  msg = "Joueur(s) enregistré(s): "
  try:
    for player in command.split(" ")[1:]:
      res.append(player.lower())
      msg+= player.lower()+", "
    msg = msg[:-2]+"\n"
    f.saveData(res,S_ACTIVE_PLAYERS)
  except Exception as e:
    msg = "ERR: setActivePlayers() - " + str(e) + "\n" + msg
  return msg
