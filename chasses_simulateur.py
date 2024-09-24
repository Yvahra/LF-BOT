from datetime import datetime, timedelta

import joueurs


LIMITE_BORNE_2 = 1000
DATA_ARMY = {
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


def approx_fdf(tdc_arrivee, tdc_chasse):
    return (156 + 4.685644*(tdc_chasse**1.105944) + 0.466*tdc_arrivee*(tdc_chasse**0.1066647)) * 0.85

def approx_tdc_chasse(tdc_arrivee:int, fdf:int) -> int:
    keep_going= True
    delta= 5
    tdc_chasse= 1
    tdc_chasse_min= 0
    tdc_chasse_max= None
    while keep_going:
        fdf_a= approx_fdf(tdc_arrivee, tdc_chasse)
        if fdf_a > fdf:
            tdc_chasse_max= tdc_chasse
            tdc_chasse= (tdc_chasse_max+tdc_chasse_min)//2
        elif fdf_a < fdf:
            if tdc_chasse_max is None:
                tdc_chasse = 2 * tdc_chasse
            else:
                tdc_chasse_min= tdc_chasse
                tdc_chasse= (tdc_chasse_max+tdc_chasse_min)//2
        else:
            keep_going= False
        if tdc_chasse_max-tdc_chasse_min < delta:
            keep_going= False

    return tdc_chasse


def simulator(joueur:joueurs.Joueur, colo:str, tdc_init:int, vt:int, nbr_chasses:int) -> list:
    # res = [ {"quantity": int, "init": int, "army":{"E": int, etc.}} ]

    # Initialisation des variables
    #nbr_chasses = vt + 1


    fdf_hb= joueur.colo1["stats_army"]["fdf_hb"] if colo.upper() == "C1" else joueur.colo2["stats_army"]["fdf_hb"]
    bonus=  0
    if not joueur.hero is None:
        bonus= 0 if joueur.hero["bonus"] != 2 else joueur.hero["level"]
    fdf_army=    fdf_hb*(1+joueur.mandibule*0.05+bonus/100)

    keep_going= True
    tdc_delta=  10000
    tdc_chasse= 10000
    fdf_chasse= None

    while keep_going:
        fdf_tot= 0
        fdf_required= []
        for i in range(nbr_chasses):
            fdf_ch=     approx_fdf(tdc_init+i*tdc_chasse,tdc_chasse)
            fdf_tot+=   fdf_ch
            fdf_required.append(fdf_ch)
        if fdf_tot < fdf_army:
            fdf_chasse= fdf_required[:]
            tdc_chasse+= tdc_delta
        else:
            keep_going= False

    if fdf_chasse is None:
        return []
    else:
        res= []
        army = joueur.colo1["army"] if colo.upper() == "C1" else joueur.colo2["army"]
        #split army in hunts
        for i in range(nbr_chasses):
            coef= fdf_chasse[i]/fdf_army
            temp_army= dict()
            for unit in army:
                temp_army[unit]= int(army[unit]*coef)
            res.append({"quantity": tdc_chasse, "init": tdc_init+i*tdc_chasse, "army":temp_army})
        return res


def tempsChasse(tdcInit: int, tdcChasse: int, vt: int) -> str:
    seconds = (60 + tdcInit / 10 + tdcChasse / 2) / (1 + vt / 10)
    # tps_chasse_conv = timedelta(seconds=tps_chasse)
    days = seconds // (24 * 3600)  # Number of days
    seconds %= (24 * 3600)
    hours = seconds // 3600  # Number of hours
    seconds %= 3600
    minutes = seconds // 60  # Number of minutes
    seconds %= 60  # Remaining seconds
    return str(int(days)) + "j " + str(int(hours)) + "h " + str(int(minutes)) + "min " + str(int(seconds)) + "s"

