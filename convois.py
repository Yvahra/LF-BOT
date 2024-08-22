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

H_CONVOIS_FILENAME = "HIST//Historique_ConvoisInternes.json"
H_DEMANDE_FILENAME = "HIST//Historique_DemandesConvois.json"
S_CONVOIS_FILENAME = "STATS//Stats_ConvoisEnCours.json"

COLONIES = f.setCOLONIES()

#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#

def printConvoisEnCours() -> str:
  global COLONIES
  data = f.loadData(S_CONVOIS_FILENAME)
  msg = """**Convoi(s) en cours**:\n"""
  for convoi in data:
    msg+= convoi["player"]["name"] + " (" + COLONIES[convoi["player"]["name"].upper()][convoi["player"]["colony"]] + ")"
    msg+= ": "+ convoi["title"]+" "+str(convoi["level"])+"\n```"
    msg+= "    P: "+ f.convertNumber(str(convoi["remaining"]["apple"])) + "\n"
    msg+= "    B: "+ f.convertNumber(str(convoi["remaining"]["wood"])) + "\n"
    msg+= "    E: "+ f.convertNumber(str(convoi["remaining"]["water"])) + "\n"
    msg+= "```"
  return msg

# 3 - `!convoi <convoyé> <C1/C2> <pomme> <bois> <eau> <convoyeur> <C1/C2>`: ajoute un convoi;
def convoi(convoyed, colo1, apple, wood, water, convoyer, colo2) -> str:
  msg = ""
  try:
    data_hist = f.loadData(H_CONVOIS_FILENAME)
    col1 = 0 if colo1 == "C1" else 1
    col2 = 0 if colo2 == "C2" else 1
    data_hist.append({
      "convoy": {"apple": int(apple),"wood": int(wood),"water": int(water)},
      "convoyer": {"name": convoyer,"colony": col1},
      "convoyed": {"name": convoyed,"colony": col2},
      "day": datetime.date.today().strftime("%Y-%m-%d")
    })
    f.saveData(data_hist, H_CONVOIS_FILENAME)
    msg = ":incoming_envelope: "+ convoyer + " a lancé " + f.convertNumber(apple) + " :apple:, " + f.convertNumber(wood) + " :wood:, et " + f.convertNumber(water) + " :droplet: à " + convoyed +"\n\n"
    
    data = f.loadData(S_CONVOIS_FILENAME)
    found = False
    for i in range(len(data)):
      print(data[i]["player"]["colony"])
      print(col1)
      if data[i]["player"]["name"].upper() == convoyed.upper() and data[i]["player"]["colony"] == col1:
        found = True
        data[i]["remaining"]["apple"] -= int(apple)
        data[i]["remaining"]["wood"] -= int(wood)
        data[i]["remaining"]["water"] -= int(water)
        if data[i]["remaining"]["apple"] < 0: data[i]["remaining"]["apple"] = 0
        if data[i]["remaining"]["wood"] < 0: data[i]["remaining"]["wood"] = 0
        if data[i]["remaining"]["water"] < 0: data[i]["remaining"]["water"] = 0
        if data[i]["remaining"]["apple"]+data[i]["remaining"]["wood"]+data[i]["remaining"]["water"] == 0:
          data.pop(i)
          msg += "Convoi terminé.\n"
        break
    if not found:
      msg = "ERR: convoi() - Convoi non trouvé.\n" + msg
    f.saveData(data, S_CONVOIS_FILENAME)
    if found:
      msg += printConvoisEnCours()+"\n"
  except Exception as e:
    msg = "ERR: convoi() - " + str(e) + "\n" + msg
  return msg


# 3 - `!autoProd <joueur> <C1/C2> <pomme> <bois> <eau>`: met à jour un convoi avec l'autoprod d'un joueur;
def autoProd(convoyed, colo1, apple, wood, water) -> str:
  msg = ""
  try:
    data_hist = f.loadData(H_CONVOIS_FILENAME)
    col1 = 0 if colo1 == "C1" else 1
    data_hist.append({
      "convoy": {"apple": int(apple),"wood": int(wood),"water": int(water)},
      "convoyer": {"name": convoyed,"colony": col1},
      "convoyed": {"name": convoyed,"colony": col1},
      "day": datetime.date.today().strftime("%Y-%m-%d")
    })
    f.saveData(data_hist, H_CONVOIS_FILENAME)
    msg = ":pick: "+ convoyed + " a produit " + f.convertNumber(apple) + " :apple:, " + f.convertNumber(wood) + " :wood:, et " + f.convertNumber(water) + " :droplet:\n\n"

    data = f.loadData(S_CONVOIS_FILENAME)
    found = False
    for i in range(len(data)):
      print(data[i]["player"]["colony"])
      print(col1)
      if data[i]["player"]["name"].upper() == convoyed.upper() and data[i]["player"]["colony"] == col1:
        found = True
        data[i]["remaining"]["apple"] -= int(apple)
        data[i]["remaining"]["wood"] -= int(wood)
        data[i]["remaining"]["water"] -= int(water)
        if data[i]["remaining"]["apple"] < 0: data[i]["remaining"]["apple"] = 0
        if data[i]["remaining"]["wood"] < 0: data[i]["remaining"]["wood"] = 0
        if data[i]["remaining"]["water"] < 0: data[i]["remaining"]["water"] = 0
        if data[i]["remaining"]["apple"]+data[i]["remaining"]["wood"]+data[i]["remaining"]["water"] == 0:
          data.pop(i)
          msg += "Convoi terminé.\n"
        break
    if not found:
      msg = "ERR: autoProd() - Convoi non trouvé.\n" + msg
    f.saveData(data, S_CONVOIS_FILENAME)
    if found:
      msg += printConvoisEnCours()+"\n"
  except Exception as e:
    msg = "ERR: autoProd() - " + str(e) + "\n" + msg
  return msg


# 1 - `!demandeConvoi <joueur> <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>`: ajoute un convoi à la liste des convois en cours;
def demandeConvoi(joueur:str, colo:str, constr:str, level:str, apple:str, wood:str, water:str) -> str: 
  msg = ""
  try:
    col = 0 if colo == "C1" else 1
    demande = {
       "title": constr,
       "level": int(level),
       "player": {
         "name": joueur,
         "colony": col
       },
       "remaining": {
         "apple": int(apple),
         "wood": int(wood),
         "water": int(water)
       }}

    data_hist = f.loadData(H_DEMANDE_FILENAME)
    data_hist.append({"date": datetime.date.today().strftime("%Y-%m-%d"),
                     "demande":demande})
    f.saveData(data_hist, H_DEMANDE_FILENAME)
    msg = "Demande enregistrée.\n"
    
    data = f.loadData(S_CONVOIS_FILENAME)
    data.append(demande)
    f.saveData(data, S_CONVOIS_FILENAME)
    msg = "Demande lancée.\n"
  except Exception as e:
    msg = "ERR: demandeConvoi() - " + str(e) + "\n" + msg
  return msg