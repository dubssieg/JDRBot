class Loader:
    """Classe de chargement des datas en un dictionnaire
    TODO permettre à l'utilisateur de choisir son fichier de données
    """
    
    def __init__(self,fichier):
        """Chargement du fichier de données en un dico de listes
        le symbole dièse sera la marque d'un commentaire dans le fichier
        
        Keywords arguments
        fichier - str, adresse d'un fichier à lire
        """
        self.dict = {}
        with open(fichier,"r", encoding="utf-8") as reader:
            for l in reader:
                if(l[0]!='#'):
                    l = l[:-1]
                    a,b = l.split(":")[0],l.split(":")[1]
                    self.dict[a] = b.split(",")