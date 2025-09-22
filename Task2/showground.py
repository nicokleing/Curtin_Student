# Student Name : Nicolas Klein
# Student ID   : 21892288



import numpy as np

class Frame:
    def __init__(self, ox, oy, w, h, color='b-'):
        self.ox, self.oy, self.w, self.h = ox, oy, w, h
        self.color = color

    def plot_me(self, p):
        ox, oy, w, h = self.ox, self.oy, self.w, self.h
        p.plot([ox, ox + w], [oy, oy], self.color)
        p.plot([ox, ox + w], [oy + h, oy + h], self.color)
        p.plot([ox, ox],     [oy, oy + h], self.color)
        p.plot([ox + w, ox + w], [oy, oy + h], self.color)

class Ship:
  
    def __init__(self, margin=0.15):
        self.margin = margin
        
        self.xlo, self.xhi, self.ylo, self.yhi = 1.0, 5.0, 0.0, 5.0
        BAR_Y = 2.2 
       
        self.parts = [
            (np.array([1, 3, 5]),  np.array([0, 5, 0]),           'purple'),   
            (np.array([2.0, 4.0]), np.array([BAR_Y, BAR_Y]),      'purple'),   
            (np.array([2.0, 4.0]), np.array([BAR_Y, BAR_Y]),      'purple'),   
            (np.array([1, 3, 5]),  np.array([3.0, 5.0, 3.0]),     'black'),
            (np.array([1, 2, 4, 5]),np.array([3.0, 2.5, 2.5, 3.0]),'black'),
            (np.array([1, 2, 4, 5]),np.array([3.0, 1.5, 1.5, 3.0]),'black'),
        ]

    def _to_box(self, x, y, ox, oy, w, h):
        m = self.margin
        xn = (x - self.xlo) / (self.xhi - self.xlo)
        yn = (y - self.ylo) / (self.yhi - self.ylo)
        xn = m + (1 - 2*m) * xn
        yn = m + (1 - 2*m) * yn
        return ox + xn*w, oy + yn*h

    def plot_in_box(self, p, ox, oy, w, h, lw=1.0):
        for x, y, c in self.parts:
            X, Y = self._to_box(x, y, ox, oy, w, h)
            p.plot(X, Y, color=c, linewidth=lw)

class Pirate:
   
    def __init__(self, xpos, ypos, width=40, height=30):
        self.xpos, self.ypos, self.width, self.height = xpos, ypos, width, height
        self.ship = Ship(margin=0.15)

    def plot_me(self, p):
      
        Frame(self.xpos, self.ypos, self.width, self.height, 'b-').plot_me(p)
   
        self.ship.plot_in_box(p, self.xpos, self.ypos, self.width, self.height, lw=1.0)

    def step_change(self):
        self.xpos += 10





