import resx.tools as t
import random

class Pnj:
    "Contient les méthodes permettant de créer un objet PnJ"

    def __init__(self,ld,current=None,change=None):
        "Initialise un nouvel objet PnJ"
        match current:
            case None:
                self.dico = ld
                self.sexe = "Féminin" if(random.randrange(2)==0) else "Masculin"
                self.name = t.Tools.gen_nom(self.sexe,self.dico)
                self.age = t.Tools.loi_normale(30,8)
                self.carac,self.constraints = t.Tools.fill_regexpr(self.dico,{'Nom' : self.name,'Age' : self.age, 'Sexe_biologique' : self.sexe})
                self.desc = ""
            case _:
                self.sexe = current.sexe
                self.name = current.name
                self.age = current.age
                match change:
                    case 'Sexe_biologique':
                        # on intervertit l'état
                        self.sexe = current.carac['Sexe_biologique'] = "Féminin" if(current.carac['Sexe_biologique']=="Masculin") else "Masculin"
                    case 'Nom':
                        # on reroll un nom
                        self.name = current.carac['Nom'] = t.Tools.gen_nom(self.sexe,self.dico,composed=True)
                    case 'Age':
                        self.age = current.carac['Age'] = t.Tools.loi_normale(30,8)
                    case car:
                        # TODO chaining des expressions par arbres
                        list_reroll = []
                        for char,filtre in current.constraints.items():
                            if (car in filtre): list_reroll.append(char)
                        blacklist = [key for key in current.carac if key != car]
                        nextchar = current.carac[car]
                        while nextchar==current.carac[car]:
                            newchars = t.Tools.fill_regexpr(self.dico,current.carac.copy(),blacklist)[0]
                            nextchar = newchars[car]
                        current.carac[car] = newchars[car]

                        # may work but need test
                        blacklist = [key for key in current.carac if key not in list_reroll]
                        newchars,self.constraints = t.Tools.fill_regexpr(self.dico,{'Nom' : self.name,'Age' : self.age, 'Sexe_biologique' : self.sexe, change : current.carac[change]},blacklist)
                        charlist = t.Tools.fill_regexpr(self.dico,{'Nom' : self.name,'Age' : self.age, 'Sexe_biologique' : self.sexe, change : current.carac[change]},["Opener","CloserM","CloserF","Middle"])[0].keys()
                        print(charlist)
                        for e in list_reroll:
                            current.carac[e] = newchars[e]

                        newdict = dict()
                        for key in charlist:
                            newdict[key] = newchars[key] if key in newchars.keys() else current.carac[key]
                        current.carac = newdict
                        
                self.carac = current.carac
                self.desc = current.desc

    def __str__(self):
        "Renvoie une description du PnJ"
        return f"{self.name} est âgé de {self.age} ans."