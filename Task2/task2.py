# Student Name : Nicolas Klein
# Student ID   : 21892288

import matplotlib.pyplot as plt
from showground import Pirate

fig = plt.figure()

pirate = Pirate(50, 30, 20, 30) 

plt.title("Showground – Task 2: Pirate with Box")
plt.xlabel("x")
plt.ylabel("y")

pirate.plot_me(plt)

plt.xlim((0, 200))
plt.ylim((0, 200))

fig.savefig("task2.png", dpi=150)
plt.show()



