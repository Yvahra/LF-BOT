##v.1.0
#   Bloc-note
##

#__________________________________________________#
## import ##
#__________________________________________________#

import datetime
import functions as f
import chasses_simulateur as simu
import joueurs

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

def convertTPSChasse(tdc_init:int, tdc_chasse:int, vt:int) -> str:
  # calcul duree des chasses
  tps_chasse = (60 + tdc_init / 10 + tdc_chasse / 2) / (1 + vt / 10)
  tps_chasse = datetime.timedelta(seconds=tps_chasse)
  return "{}".format(tps_chasse)


  # !simuChasse <tdc_initial> <tdc_total_chassé> <colonie_de_chasse>
def simuChasse(joueur:str, tdc_init:str, colo:str, vt:str, nb_chasses:str) -> str:
  msg= "Chasse impossible."
  chasses= simu.simulator(joueurs.Joueur(joueur),colo,int(tdc_init),int(vt),int(nb_chasses))
  # res = [ {"quantity": int, "init": int, "army":{"E": int, etc.}} ]
  if len(chasses) > 0:
    msg_temp= ""
    tdc_chasse= 0
    for chasse in chasses:
      msg_temp+= "    Quantité chassée: "+f.betterNumber(str(chasse["quantity"]))
      msg_temp+= " ("+f.betterNumber(str(chasse["init"])) + " -> " + f.betterNumber(str(chasse["init"]+chasse["quantity"]))+")\n"
      msg_temp+= "```"
      for unit in chasse["army"]:
        msg_temp+=unit + ": " + str(chasse["army"][unit])+"\n"
      tdc_chasse+= "```" + str(chasse["quantity"]) + "\n\n"
    msg= "# Résultats du simulateur de chasses\n"
    msg+="Joueur:     " + joueur + " (" + colo + ")\n"
    msg+="TdC Chassé: " + f.betterNumber(str(tdc_chasse)) + "\n" + msg_temp
  return msg