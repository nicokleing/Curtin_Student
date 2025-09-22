# Student Name : Ima Student
# Student ID   : 12345678

import matplotlib.pyplot as plt
from showground import Pirate

pirate1 = Pirate(40,60)

#plt.ion()
plt.title("Showground")

for t in range(1):
    pirate1.step_change()
    pirate1.plot_me(plt)
    
    plt.xlim((0,200))
    plt.ylim((0,200))

    #plt.pause(0.5)
    #plt.cla()
    plt.show()

#plt.ioff()
