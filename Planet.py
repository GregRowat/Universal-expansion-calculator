class Planet:
    def __init__(self, name, mass, distance):
        self.name = name
        self.mass = mass
        self.distance = distance

    def __str__(self):
        return self.name
