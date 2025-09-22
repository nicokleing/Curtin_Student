# Student Name : Nicolas Klein
# Student ID   : 21892288


import matplotlib.pyplot as plt
from showground import Pirate

fig = plt.figure()

pirate = Pirate(50, 30, 20, 30)


plt.title("Showground – Task 1: Pirate with Box")
plt.xlabel("X")
plt.ylabel("Y")

for t in range(1):
    pirate.step_change()
    pirate.plot_me(plt)
    
    plt.xlim((0, 200))
    plt.ylim((0, 200))

fig.savefig("task1.png", dpi=150)

plt.show()



