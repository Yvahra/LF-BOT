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

H_CHASSE_FILENAME = "HIST//Historique_Chasses.json"
S_JOUEUR_FILENAME = "STATS//Stats_Joueurs.json"

COLONIES = f.setCOLONIES()

#__________________________________________________#
## FONCTIONS GENERIQUES ##
#__________________________________________________#

def printChasses(joueur:str) -> str:
  global COLONIES
  data = f.loadData(H_CHASSE_FILENAME)
  msg = "**Chasses de "+joueur+"**:\n```"
  for c in data:
    if c["player"].upper() == joueur.upper():
      msg+= "["+ c["day"] +"] +"+ f.convertNumber(str(c["quantity"])) + "cm² " + "\n"
  msg+= "```"
  return msg


# 3 - `!chasse <joueur> <C1/C2> <quantité>`: enregistre une chasse;
def chasse(joueur:str, quantity:str):
  msg = ""
  try:
    data = f.loadData(H_CHASSE_FILENAME)
    data.append({
                 "player": joueur,
                 "quantity": int(quantity),
                 "day": datetime.date.today().strftime("%Y-%m-%d")
               })
    f.saveData(data, H_CHASSE_FILENAME)
    msg = "Chasse enregistrée avec succès"
  except Exception as e:
    msg = "ERR: chasse() - " + str(e)
  return msg
  