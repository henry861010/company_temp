class Face:
    def __init__(self, type:str="", dim:list=[]):
        self.type = type
        self.dim = dim
        
    def set(self, type:str, dim:list):
        self.type = type
        self.dim = dim
        
    '''
        set by the dict {
            "type": BOX/CLINDER/POLYGON
            "dim: []
        }
    '''
    def set_dict(self, face_dict:dict):
        self.type = face_dict["type"]
        self.dim = face_dict["dim"]
        
        