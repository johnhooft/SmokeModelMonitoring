class smoke:
    def __init__(self, timestamp, prob=None, imagecurr=None, imageprev=None, imagenext=None) -> None:
        self.timestamp = timestamp
        self.prob = prob
        self.imagecurr = imagecurr
        self.imageprev = imageprev
        self.imagenext = imagenext

    def print(self):
        print("\n")
        print("Time stamp: " +str(self.timestamp))
        if self.prob: print("Smoke Prob: "+str(self.prob))
        if self.imagecurr: print("Image current: "+self.imagecurr)
        if self.imageprev: print("Image prev: "+self.imageprev)
        if self.imagenext: print("Image prev: "+self.imagenext)
        print("\n")