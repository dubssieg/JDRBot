class StatgetterException(Exception):
    def __init__(self, value="Impossible de récupérer la valeur."):
        self.value = value

    def __str__(self):
        return repr(self.value)
