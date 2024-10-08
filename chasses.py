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
def simuChasse(joueur:str, tdc_init:str, colo:str, vt:str, nb_chasses:str) -> list[str]:
  msg= ["Chasse impossible."]
  chasses= simu.simulator(joueurs.Joueur(joueur),colo,int(tdc_init),int(vt),min(int(nb_chasses),int(vt)+1))
  # res = [ {"quantity": int, "init": int, "army":{"E": int, etc.}} ]
  if len(chasses) > 0:
    msg_temp= []
    tdc_chasse= 0
    init= chasses[0]["init"]
    for chasse in chasses:
      msg_temp.append(" - Quantité chassée: "+f.betterNumber(str(chasse["quantity"])))
      msg_temp[-1]+= " ("+f.betterNumber(str(chasse["init"])) + " -> " + f.betterNumber(str(chasse["init"]+chasse["quantity"])) +")"
      msg_temp[-1]+=  " en " + simu.tempsChasse(init, chasse["quantity"], int(vt)) + "\n"
      msg_temp.append("```")
      for unit in chasse["army"]:
        msg_temp[-1]+=unit + ": " + str(chasse["army"][unit])+"\n"
      msg_temp[-1]+= "```"
      tdc_chasse+= chasse["quantity"]
    msg= ["# Résultats du simulateur de chasses\n"]
    msg[-1]+="**Joueur**:     " + joueur + " (" + colo + ")\n"
    msg[-1]+="**TdC Chassé**: " + f.betterNumber(str(tdc_chasse)) + " en " + str(len(chasses)) + " chasse(s)\n"
    msg= msg+msg_temp
  return msg

  # !simuChassePex <tdc_initial> <tdc_total_chassé> <colonie_de_chasse>
def simuChassePex(joueur:str, tdc_init:str, tdc_chasse:str, colo:str, vt:str, nb_chasses:str) -> list[str]:
  msg= ["Chasse impossible."]
  chasses= simu.simulatorPex(joueurs.Joueur(joueur),colo,int(tdc_init),int(tdc_chasse),min(int(nb_chasses),int(vt)+1))
  # res = [ {"quantity": int, "init": int, "army":{"E": int, etc.}} ]
  if len(chasses) > 0:
    msg_temp= []
    tdc_chasse= 0
    init= chasses[0]["init"]
    for chasse in chasses:
      msg_temp.append(" - Quantité chassée: "+f.betterNumber(str(chasse["quantity"])))
      msg_temp[-1]+= " ("+f.betterNumber(str(chasse["init"])) + " -> " + f.betterNumber(str(chasse["init"]+chasse["quantity"])) +")"
      msg_temp[-1]+=  " en " + simu.tempsChasse(init, chasse["quantity"], int(vt)) + "\n"
      msg_temp.append("```")
      for unit in chasse["army"]:
        msg_temp[-1]+=unit + ": " + str(chasse["army"][unit])+"\n"
      msg_temp[-1]+= "```"
      tdc_chasse+= chasse["quantity"]
    msg= ["# Résultats du simulateur de chasses\n"]
    msg[-1]+="**Joueur**:     " + joueur + " (" + colo + ")\n"
    msg[-1]+="**TdC Chassé**: " + f.betterNumber(str(tdc_chasse)) + " en " + str(len(chasses)) + " chasse(s)\n"
    msg= msg + msg_temp
  return msg