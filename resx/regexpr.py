class Regexpr:
    "Classe permettant la modélisation d'expression régulières"

    def res(expr,dico):
        """Fonction permettant l'évaluation d'une expression régulière

        Keywords arguments:
        expr - un objet de type Regexpr
        dico - un dictionnaire, données d'exécution du programme
        """
        match expr:
            case Regexpr.Or(expr1,expr2):
                return (Regexpr.res(expr1,dico) or Regexpr.res(expr2,dico))
            case Regexpr.And(expr1,expr2):
                return (Regexpr.res(expr1,dico) and Regexpr.res(expr2,dico))
            case Regexpr.Vide():
                return True
            case Regexpr.Element(cle,comparateur,valeur):
                return Regexpr.evaluate(cle,comparateur,valeur,dico)
            case True | False:
                return expr
            case _:
                return False

    def evaluate(filtre,comparateur,val,dico):
        """Evalue le résultat d'une condition locale, et renvoie sa validité
        
        Keywords arguments:
        filtre - str, clé pouvant ou non être présente dans la dico
        comparateur - str, opérateur
        val - str, valeur associée au filtre à chercher dans le dico
        dico - un dictionnaire, données d'exécution du programme
        """
        if(filtre in dico.keys()):
            if(comparateur=="==" and dico[filtre]==val[1:-1]) or (comparateur=="!=" and dico[filtre]!=val[1:-1]) or (comparateur==">=" and int(dico[filtre])>=int(val)) or (comparateur=="<=" and int(dico[filtre])<=int(val)):
                return True
        return False

    class Or:
        "Opérateur logique OU"
        __match_args__ = ("a", "b") 
        def __init__(self,expr1,expr2):
            self.a = expr1
            self.b = expr2
        
        def __str__(self):
            return f"Or({self.a},{self.b})"

    class And:
        "Opérateur logique ET"
        __match_args__ = ("a", "b") 
        def __init__(self,expr1,expr2):
            self.a = expr1
            self.b = expr2

        def __str__(self):
            return f"And({self.a},{self.b})"

    class Element:
        "Element, plus bas niveau d'existence"
        __match_args__ = ("a","comp","b") 
        def __init__(self,cle,comparateur,valeur):
            self.a = cle
            self.comp = comparateur
            self.b = valeur

        def __str__(self):
            return f"{self.a} {self.comp} {self.b}"

    class Vide:
        "Modélise le vide"
        def __init__(self):
            pass
        
        def __str__(self):
            return "NA"