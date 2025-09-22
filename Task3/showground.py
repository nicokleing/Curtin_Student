# Student Name : Nicolas Klein
# Student ID   : 21892288



import numpy as np

class Frame:
    def __init__(self, ox, oy, w, h, color='b', lw=1.2):
        self.ox, self.oy, self.w, self.h = ox, oy, w, h
        self.color = color
        self.lw = lw

    def plot_me(self, p):
        ox, oy, w, h = self.ox, self.oy, self.w, self.h
        p.plot([ox, ox + w], [oy, oy], color=self.color, linewidth=self.lw)
        p.plot([ox, ox + w], [oy + h, oy + h], color=self.color, linewidth=self.lw)
        p.plot([ox, ox],     [oy, oy + h], color=self.color, linewidth=self.lw)
        p.plot([ox + w, ox + w], [oy, oy + h], color=self.color, linewidth=self.lw)

class Ship:

    def __init__(self, margin=0.15, accent_color='red', hull_color='black', lw=1.6):
        self.margin = margin
        self.accent_color = accent_color
        self.hull_color = hull_color
        self.lw = lw

        self.xlo, self.xhi, self.ylo, self.yhi = 1.0, 5.0, 0.0, 5.0
        BAR_Y = 2.2

        self.parts = [
            (np.array([1, 3, 5]),  np.array([0, 5, 0]),          'accent'),        
            (np.array([2.0, 4.0]), np.array([BAR_Y, BAR_Y]),     'accent'),                  
            (np.array([2.0, 4.0]), np.array([BAR_Y, BAR_Y]),     'accent'),         
            (np.array([1, 3, 5]),    np.array([3.0, 5.0, 3.0]),    'hull'),
            (np.array([1, 2, 4, 5]), np.array([3.0, 2.5, 2.5, 3.0]),'hull'),
            (np.array([1, 2, 4, 5]), np.array([3.0, 1.5, 1.5, 3.0]),'hull'),
        ]

    def _to_box(self, x, y, ox, oy, w, h):
        m = self.margin
        xn = (x - self.xlo) / (self.xhi - self.xlo)
        yn = (y - self.ylo) / (self.yhi - self.ylo)
        xn = m + (1 - 2*m) * xn
        yn = m + (1 - 2*m) * yn
        return ox + xn*w, oy + yn*h

    def plot_in_box(self, p, ox, oy, w, h):
        for x, y, role in self.parts:
            X, Y = self._to_box(x, y, ox, oy, w, h)
            color = self.accent_color if role == 'accent' else self.hull_color
            p.plot(X, Y, color=color, linewidth=self.lw)

class Pirate:
    def __init__(self, xpos, ypos, width=40, height=30,
                 frame_color='tab:blue', accent_color='red',
                 margin=0.15, lw=1.6):
        self.xpos, self.ypos = xpos, ypos
        self.width, self.height = width, height
        self.frame_color = frame_color
        self.ship = Ship(margin=margin, accent_color=accent_color,
                         hull_color='black', lw=lw)

    def plot_me(self, p):
        Frame(self.xpos, self.ypos, self.width, self.height,
              color=self.frame_color, lw=self.ship.lw).plot_me(p)
        self.ship.plot_in_box(p, self.xpos, self.ypos, self.width, self.height)

    def step_change(self):
        self.xpos += 10





