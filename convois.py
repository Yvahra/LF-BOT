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
H_RSS_PARTAGEES_FILENAME = "HIST//Historique_RessourcesPartagees.json"
S_CONVOIS_FILENAME = "STATS//Stats_ConvoisEnCours.json"
S_JOUEUR_FILENAME = "STATS//Stats_Joueurs.json"
S_ACTIVE_PLAYERS = "STATS//Stats_JoueursActifs.json"

COLONIES = f.setCOLONIES()

#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#

def updateConvoi(player, apple, wood, water) -> bool:
  data = f.loadData(S_CONVOIS_FILENAME)
  found = False
  for i in range(len(data)):
    if data[i]["player"]["name"].upper() == player.upper() and not found:
      found = True
      data[i]["remaining"]["apple"] -= int(apple)
      data[i]["remaining"]["wood"] -= int(wood)
      data[i]["remaining"]["water"] -= int(water)
      if data[i]["remaining"]["apple"] < 0: data[i]["remaining"]["apple"] = 0
      if data[i]["remaining"]["wood"] < 0: data[i]["remaining"]["wood"] = 0
      if data[i]["remaining"]["water"] < 0: data[i]["remaining"]["water"] = 0
      if data[i]["remaining"]["apple"] + data[i]["remaining"]["wood"] + data[i]["remaining"]["water"] == 0:
        data.pop(i)
      break
  f.saveData(data, S_CONVOIS_FILENAME)
  return found


def printConvoisEnCours() -> str:
  global COLONIES
  data = f.loadData(S_CONVOIS_FILENAME)
  msg = """**Convoi(s) en cours**:\n"""
  for convoi in data:
    msg+= convoi["player"]["name"] + " (" + COLONIES[convoi["player"]["name"].upper()][convoi["player"]["colony"]] + ")"
    msg+= ": "+ convoi["title"]+" "+str(convoi["level"])+"\n```"
    msg+= "    P: "+ f.betterNumber(str(convoi["remaining"]["apple"])) + "\n"
    msg+= "    B: "+ f.betterNumber(str(convoi["remaining"]["wood"])) + "\n"
    msg+= "    E: "+ f.betterNumber(str(convoi["remaining"]["water"])) + "\n"
    msg+= "```"
  return msg


# `!convoi [convoyeur] <convoyé> <pomme> <bois> <eau>`: ajoute un convoi;
def convoi(convoyer, convoyed, apple, wood, water) -> str:
  msg = ""
  try:
    data_hist = f.loadData(H_CONVOIS_FILENAME)
    data_hist.append({
      "convoy": {"apple": int(apple),"wood": int(wood),"water": int(water)},
      "convoyer": convoyer,
      "convoyed": convoyed,
      "day": datetime.date.today().strftime("%Y-%m-%d")
    })
    f.saveData(data_hist, H_CONVOIS_FILENAME)
    msg = ":incoming_envelope: "+ convoyer + " a lancé " + f.betterNumber(apple) + " :apple:, " + f.betterNumber(wood) + " :wood:, et " + f.betterNumber(water) + " :droplet: à " + convoyed +"\n\n"
    
    found = updateConvoi(convoyed, apple, wood, water)

    if not found:
      msg = "ERR: convoi() - Convoi non trouvé.\n" + msg
    if found:
      msg += printConvoisEnCours()+"\n"
  except Exception as e:
    msg = "ERR: convoi() - " + str(e) + "\n" + msg
  return msg


# 3 - `!autoProd [joueur] <pomme> <bois> <eau>`: met à jour un convoi avec l'autoprod d'un joueur;
def autoProd(convoyed, apple, wood, water) -> str:
  msg = ""
  try:
    data_hist = f.loadData(H_CONVOIS_FILENAME)
    data_hist.append({
      "convoy": {"apple": int(apple),"wood": int(wood),"water": int(water)},
      "convoyer": convoyed,
      "convoyed": convoyed,
      "day": datetime.date.today().strftime("%Y-%m-%d")
    })
    f.saveData(data_hist, H_CONVOIS_FILENAME)
    msg = ":pick: "+ convoyed + " a produit " + f.convertNumber(apple) + " :apple:, " + f.convertNumber(wood) + " :wood:, et " + f.convertNumber(water) + " :droplet:\n\n"

    found = updateConvoi(convoyed, apple, wood, water)

    if not found:
      msg = "ERR: autoProd() - Convoi non trouvé.\n" + msg
    if found:
      msg += printConvoisEnCours()+"\n"
  except Exception as e:
    msg = "ERR: autoProd() - " + str(e) + "\n" + msg
  return msg


# 1 - `!demandeConvoi <joueur> <C1/C2> <construction/recherche> <niveau> <pomme> <bois> <eau>`: ajoute un convoi à la liste des convois en cours;
def demandeConvoi(joueur:str, colo:str, constr:str, level:str, apple:str, wood:str, water:str) -> str: 
  msg = ""
  try:
    convois = f.loadData(S_CONVOIS_FILENAME)
    found = False
    for i in range(len(convois)):
      if convois[i]["player"]["name"].upper() == joueur.upper() and not found:
        found = True
    if found:
      msg = 'ERR: un convoi est déjà en cours pour ce joueur'
    else:
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

def repartitionRessources(dateRecap:str):
  msg = ""
  try:
    active_players = f.loadData(S_ACTIVE_PLAYERS)
    nb_joueurs_actifs = len(active_players)
    prod_totale = 0
    ressources_detail = {}

    convois = f.loadData(H_CONVOIS_FILENAME)
    for convoi in convois:
      if convoi["day"] == dateRecap and convoi["convoyer"].lower() in active_players and convoi["convoyed"].lower() in active_players:
        q = convoi["convoy"]["apple"] + convoi["convoy"]["wood"] + convoi["convoy"]["water"]
        if not convoi["convoyer"].lower() in ressources_detail:
          ressources_detail[convoi["convoyer"].lower()] = { "convois": [0,0], #reçu, donné
                                                            "exploit": 0,
                                                            "pillage": 0}
        if not convoi["convoyed"].lower() in ressources_detail:
          ressources_detail[convoi["convoyed"].lower()] = { "convois": [0,0], #reçu, donné
                                                            "exploit": 0,
                                                            "pillage": 0}
        ressources_detail[convoi["convoyed"].lower()]["convois"][0] += q
        ressources_detail[convoi["convoyer"].lower()]["convois"][1] += q

    players = f.loadData(S_JOUEUR_FILENAME)
    for player in players:
      vass1 = False
      vass2 = False
      if not player["name"].lower() in ressources_detail:
        ressources_detail[player["name"].lower()] = {"convois": [0,0], #reçu, donné
                                                     "exploit": 0,
                                                     "pillage": 0}
      if player["colo1"]["vassal"]["name"].lower() in active_players:
          vass1 = True
          if not player["colo1"]["vassal"]["name"].lower() in ressources_detail:
            ressources_detail[player["colo1"]["vassal"]["name"].lower()] = { "convois": [0,0], #reçu, donné
                                                                             "exploit": 0,
                                                                             "pillage": 0}
      if player["colo2"]["vassal"]["name"].lower() in active_players:
          vass2 = True
          if not player["colo2"]["vassal"]["name"].lower() in ressources_detail:
            ressources_detail[player["colo2"]["vassal"]["name"].lower()] = { "convois": [0,0], #reçu, donné
                                                                             "exploit": 0,
                                                                             "pillage": 0}

      prodC1 = player["colo1"]["exploitation"] * 24
      prodC2 = player["colo2"]["exploitation"] * 24
      prod_totale += player["colo1"]["exploitation"] * 24 + player["colo2"]["exploitation"] * 24
      if vass1:
        prop_pille = (player["colo1"]["vassal"]["pillage"]+20) / 100
        ressources_detail[player["name"].lower()]["exploit"] +=  prodC1 * (1 - prop_pille)
        ressources_detail[player["colo1"]["vassal"]["name"].lower()]["pillage"] += prodC1 * prop_pille
      else:
        ressources_detail[player["name"].lower()]["exploit"] +=  prodC1
      if vass2:
        prop_pille = (player["colo2"]["vassal"]["pillage"]+20) / 100
        ressources_detail[player["name"].lower()]["exploit"] +=  prodC2 * (1 - prop_pille)
        ressources_detail[player["colo2"]["vassal"]["name"].lower()]["pillage"] += prodC2 * prop_pille
      else:
        ressources_detail[player["name"].lower()]["exploit"] +=  prodC2

    last_recap_found = False
    nb_jour = 1
    ress_parta = f.loadData(H_RSS_PARTAGEES_FILENAME)
    cumul = {}
    while not last_recap_found:
      if (datetime.datetime.strptime(dateRecap, "%Y-%m-%d") - datetime.timedelta(days=nb_jour)).strftime("%Y-%m-%d") in ress_parta:
        last_recap_found = True
        cumul = ress_parta[(datetime.datetime.strptime(dateRecap, "%Y-%m-%d") - datetime.timedelta(days=nb_jour)).strftime("%Y-%m-%d")]["cumul"]
      else:
        nb_jour += 1

    salaire = int(prod_totale / nb_joueurs_actifs)

    for player in active_players:
      if not player.lower() in cumul :
        cumul[player.lower()] = 0
      if player.lower() in ressources_detail:
        cumul[player.lower()] += ressources_detail[player.lower()]["exploit"]
        cumul[player.lower()] += ressources_detail[player.lower()]["pillage"]
        cumul[player.lower()] += ressources_detail[player.lower()]["convois"][0]
        cumul[player.lower()] -= ressources_detail[player.lower()]["convois"][1]
      cumul[player.lower()] -= salaire

    recap = {
      "salaire": salaire,
      "ressources_detail": ressources_detail,
      "cumul": cumul
    }

    ress_parta[dateRecap] = recap
    f.saveData(ress_parta, H_RSS_PARTAGEES_FILENAME)

    msg = printRessourcesPartagees(dateRecap)

  except Exception as e:
    msg = "ERR: repartitionRessources() - " + str(e) + "\n" + msg
  return msg

def printRessourcesPartagees(dateRecap:str) -> str:
  msg = ""
  try:
    ress = f.loadData(H_RSS_PARTAGEES_FILENAME)[dateRecap]
    msg = "# Récapitulatif des ressources partagées\n\n"
    msg+= "Salaire: " + f.betterNumber(str(int(ress["salaire"]))) +  " ressources\n"
    for player in ress["ressources_detail"]:
      msg+= "``` * "+ player.upper() + ":\n"
      msg+= "Ressources exploitées :           "+ f.betterNumber(str(int(ress["ressources_detail"][player]["exploit"]))) + "\n"
      msg+= "Ressources livrées par le joueur: "+ f.betterNumber(str(int(ress["ressources_detail"][player]["convois"][1]))) + "\n"
      msg+= "Ressources livrées au joueur:     "+ f.betterNumber(str(int(ress["ressources_detail"][player]["convois"][0]))) + "\n"
      msg+= "Ressources pillées par le joueur: "+ f.betterNumber(str(int(ress["ressources_detail"][player]["pillage"]))) + "\n"
      msg+= "```\n"
    msg+= "```\n"
    MSG = ["",""]
    for player in ress["cumul"]:
      if ress["cumul"][player] < 0:
        MSG[0]+= player + " doit percevoir " + f.betterNumber(str(int(-ress["cumul"][player]))) + " ressources\n"
      else:
        MSG[1]+= player + " doit rendre " + f.betterNumber(str(int(ress["cumul"][player]))) + " ressources\n"
    msg+= MSG[0]+"\n"+MSG[1]
    msg+= "```"

  except Exception as e:
    msg = "ERR printRessourcesPartagees() - " + str(e) + "\n" + msg

  return msg


def convoisDuJour(date:str):
  msg = "## Convois effectué le " + date + "\n```"
  try:
    convois = f.loadData(H_CONVOIS_FILENAME)
    msg_temp = {}
    qc = {}
    for convoi in convois:
      if date == convoi["day"]:
        convoyer = convoi["convoyer"]
        if not convoyer in msg_temp: msg_temp[convoyer] = ""
        if not convoyer in qc: qc[convoyer] = 0
        msg_temp[convoyer] = "- " + convoi["convoyed"] + " a reçu " + f.betterNumber(str(qc[convoyer])) + " ressources \n"
        qc[convoyer] +=  qc[convoyer]

    for convoyer in msg_temp:
      msg+= convoyer + ": " + f.betterNumber(str(qc[convoyer])) + " ressources (Total)\n"
      msg+= msg_temp[convoyer]+"\n"

    if msg[-1] == "`": msg+="Aucun convoi."
    msg += "```"
  except Exception as e:
    msg = "ERR: convoi() - " + str(e) + "\n" + msg
  return msg