class MinecraftPlayer(object): 
    """Simple class for keeping track of a player's state""" 
    def __init__(self):
        self.x_coord = 0 
        self.y_coord = 0 
        self.z_coord = 0 
    
    def update_position(self, coords: list): 
        """
        Update the player's position coordinates for tracking position updates.     
        """
        if len(coords) == 3: 
            self.x_coord = coords[0] 
            self.y_coord = coords[1] 
            self.z_coord = coords[2] 
             
        else:
            raise(ValueError, "Improper Coordinate List Length")

    @property 
    def position(self): 
        return (self.x_coord, self.y_coord, self.z_coord)
        
