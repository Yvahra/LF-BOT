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

H_ALLIANCE_FILENAME = "HIST//Historique_Alliance.json"
S_ALLIANCE_FILENAME = "STATS//Stats_Alliance.json"

#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#


def printAlliance() -> str:
  data = f.loadData(S_ALLIANCE_FILENAME)
  msg = """**Statistiques LF**:\n```"""
  msg+= "    Membre: "+ str(data["members"])+"\n"
  msg+= "    TDC:    "+f.convertNumber(str(data["tdc"]))+"\n"
  msg+= "    Bonus:\n"
  msg+= "        Health:  +"+str(data["bonus"]["health"])+"%\n"
  msg+= "        Convois: +"+str(data["bonus"]["convoy"]*10)+"%\n"
  msg+= "        TDP:     -"+str(data["bonus"]["tdp"])+"%\n"
  msg+= "        Membres: +"+str(data["bonus"]["members"])+" membres\n```"
  return msg


def snapshot() -> str:
  msg = ""
  try:
    today = datetime.date.today()
    snapshot = f.loadData(S_ALLIANCE_FILENAME)
    data = f.loadData(H_ALLIANCE_FILENAME)
    data.append({"date":today.strftime("%Y-%m-%d"), "snapshot":snapshot})
    f.saveData(data, H_ALLIANCE_FILENAME)
    msg = "Snapshot enregistré avec succès."  
  except Exception as e:
    msg = "ERR: snapshot() - " + str(e)
  return msg


def setTDC(tdc:str) -> str:
  err = snapshot()
  if err.startswith("ERR"):
    return err
  data = f.loadData(S_ALLIANCE_FILENAME)
  msg = ""
  try:
    data["tdc"] = int(tdc)
    msg = "TDC modifié avec succès."
    f.saveData(data, S_ALLIANCE_FILENAME)
  except Exception as e:
    msg = "ERR: setTDC() - " + str(e)
  return msg



# 3 - `!setNBMembre <quantité>`: modifie le nombre de joueurs de l'alliance;
def setNBMembre(nbMembre:str) -> str:
  err = snapshot()
  if err.startswith("ERR"):
    return err
  data = f.loadData(S_ALLIANCE_FILENAME)
  msg = ""
  try:
    data["members"] = int(nbMembre)
    msg = "Nombre de membres modifié avec succès."
    f.saveData(data, S_ALLIANCE_FILENAME)
  except Exception as e:
    msg = "ERR: setNBMembre() - " + str(e)
  return msg


# 3 - `!setBonusAlly <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`: modifie le bonus d'alliance;
def setBonusAlly(health:str, convoi:str, tdp:str, membre:str) -> str:
  err = snapshot()
  if err.startswith("ERR"):
    return err
  data = f.loadData(S_ALLIANCE_FILENAME)
  msg = ""
  try:
    data["bonus"] = {
      "health": int(health), 
      "convoy": int(convoi), 
      "tdp": int(tdp), 
      "members": int(membre)
    }
    msg = "Nombre de membres modifié avec succès."
    f.saveData(data, S_ALLIANCE_FILENAME)
  except Exception as e:
    msg = "ERR: setBonusAlly() - " + str(e)
  return msg


# 3 - `!setAlly <tdc> <nbMembres> <niveauVie> <niveauConvois> <niveauTDP> <niveauMembres>`: modifie les stats de l'alliance;
def setAlly(tdc:str, nbmembre:str, health:str, convoi:str, tdp:str, membre:str) -> str:
  err = snapshot()
  if err.startswith("ERR"):
    return err
  data = f.loadData(S_ALLIANCE_FILENAME)
  msg = ""
  try:
    data["tdc"] = tdc
    data["members"] = nbmembre
    data["bonus"] = {
      "health": int(health), 
      "convoy": int(convoi), 
      "tdp": int(tdp), 
      "members": int(membre)
    }
    msg = "Nombre de membres modifié avec succès."
    f.saveData(data, S_ALLIANCE_FILENAME)
  except Exception as e:
    msg = "ERR: setAlly() - " + str(e)
  return msg