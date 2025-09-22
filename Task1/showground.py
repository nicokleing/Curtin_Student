# Student Name : Nicolas Klein
# Student ID   : 21892288


class Pirate():
   

    def __init__(self, xpos, ypos, width=40, height=30):
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height
        
    def plot_me(self, p):
        ox, oy = self.xpos, self.ypos
        w, h = self.width, self.height
        
        p.plot([ox, ox + w], [oy, oy], 'b-')
        p.plot([ox, ox + w], [oy + h, oy + h], 'b-')
        p.plot([ox, ox], [oy, oy + h], 'b-')
        p.plot([ox + w, ox + w], [oy, oy + h], 'b-')
        
        
    def step_change(self):
        self.xpos = self.xpos + 10




