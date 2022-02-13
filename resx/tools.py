import random
import numpy
import resx.regexpr as r

class Tools:
    "Contient des méthodes de calcul et de génération"

    def conversion(string):
        # quand on arrive ici, on considère que la chaine est chainée
        #ischained = ('|' in string)
        #isproba = ('%' in string)
        string = string.replace('|','').replace('%','') # on supprime les tags
        islogical = ('&' in string) or ('$' in string)
        hasparenthesis = ('(' in string) or (')' in string)
        match [islogical,hasparenthesis]:
            case [_,False]:
                liste = string.split(' ')
                return Tools.conv(liste) # lecture gauche à droite, pas de prio opératoire
            case [True,True]:
                pass # pour le moment on gère pas des parenthèses

    def conv(liste):
        if(len(liste)>3):
            if(liste[3]=='&'): return r.Regexpr.And(r.Regexpr.Element(liste[0],liste[1],liste[2]),Tools.conv(liste[4:]))
            if(liste[3]=='$'): return r.Regexpr.Or(r.Regexpr.Element(liste[0],liste[1],liste[2]),Tools.conv(liste[4:]))
        else:
            return r.Regexpr.Element(liste[0],liste[1],liste[2])

    def loi_normale(mu, sigma):
        "Renvoie le premier entier strictement positif généré selon une loi normale."
        n = 0
        while (n<=0):
            n = numpy.random.normal(sigma,mu,1)[0]
        return int(n)

    def weighted_choice(keys,probas):
        "Sélectionne une clé en fonction d'un poids de probabilité"
        cumulatedProbas,summ = [],0
        for e in probas:
            cumulatedProbas.append(e+summ)
            summ+=e
        maximum = cumulatedProbas[-1]
        select = random.randint(0,maximum)
        i = 0
        while i<len(probas):
            if (cumulatedProbas[i] > select): return keys[i]
            i+=1 # retourne la première occurence d'un nombre inférieur
        return keys[-1] # ou la dernière occurence de la liste sinon

    def gen_nom(sexe,ld,composed=True,neuralInput=False):
        "Sexe biologique doit être au format Masculin ou Féminin"
        opener,closer,mid1,mid2,a = random.choice(ld.dict["Opener"]),random.choice(ld.dict["Closer"+sexe[0]]),random.choice(ld.dict["Middle"]),random.choice(ld.dict["Middle"]),random.randrange(3)
        if(neuralInput): # renvoie une liste
            pass
            """
            if(a==0): return (NeuralPrep.convert_to_ints(opener+mid1+mid2+closer),opener+mid1+mid2+closer)
            elif(a==1): return (NeuralPrep.convert_to_ints(opener+mid1+closer),opener+mid1+closer)
            else: return (NeuralPrep.convert_to_ints(opener+closer),opener+closer)
            """
        elif(composed): # renvoie un nom
            if(a==0): return opener+mid1+mid2+closer
            elif(a==1): return opener+mid1+closer
            else: return opener+closer
        else:
            if(a==0): return f"{opener},{mid1},{mid2},{closer},{opener}{mid1}{mid2}{closer},{sexe[0]}"
            elif(a==1): return f"{opener},{mid1},,{closer},{opener}{mid1}{closer},{sexe[0]}"
            else: return f"{opener},,,{closer},{opener}{closer},{sexe[0]}"

    def fill_regexpr(ld,dico,blacklist=["Opener","CloserM","CloserF","Middle"]):
        "Effectue une attribution des caractéristiques annexes"
        constraints = dict()
        for key in ld.dict:
            if(key not in blacklist):
                if('%' in key):
                    if('|' in key):
                        probas,valeurs = [],[]
                        for e in ld.dict[key]:
                            probas.append(int(e.split('%')[0]))
                            valeurs.append(e.split('%')[1])
                        # caractère chainé en fonction d'une autre caractéristique + proba
                        # print(f"PROBAS {probas} > VALEURS : {valeurs}")
                        test,cle = key.split('~')[0],key.split('~')[1]
                        if(r.Regexpr.res(Tools.conversion(test),dico)):
                            dico[cle] = Tools.weighted_choice(valeurs,probas)
                            constraints[cle] = test
                    else:
                        # on doit sélectionner selon une probabilité simple
                        probas,valeurs = [],[]
                        for e in ld.dict[key]:
                            probas.append(int(e.split('%')[0]))
                            valeurs.append(e.split('%')[1])
                        dico[key[1:]] = Tools.weighted_choice(valeurs,probas)
                elif(key[0]=='|'):
                    # caractère chainé en fonction d'une autre caractéristique
                    test,cle = key.split('~')[0],key.split('~')[1]
                    if(r.Regexpr.res(Tools.conversion(test),dico)):
                        dico[cle] = random.choice(ld.dict[key])
                        constraints[cle] = test
                else:
                    # sélection aléatoire basique
                    dico[key] = random.choice(ld.dict[key])
        return (dico,constraints)
