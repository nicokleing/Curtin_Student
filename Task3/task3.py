# Student Name : Nicolas Klein
# Student ID   : 21892288

import matplotlib.pyplot as plt
from showground import Pirate

fig = plt.figure()

pirates = [
    Pirate(50, 30, 20, 30,  frame_color='tab:blue',   accent_color='purple', margin=0.18),
    Pirate(105, 10, 40, 50, frame_color='tab:orange', accent_color='green', margin=0.15),
    Pirate(150, 80, 40, 80, frame_color='tab:green',  accent_color='red', margin=0.22),
]

plt.title("Showground - Task 3: Three colourful pirate ships")
plt.xlabel("x"); plt.ylabel("y")

for p in pirates:
    p.plot_me(plt)

plt.xlim((0, 200)); plt.ylim((0, 200))
fig.savefig("task3.png", dpi=150)
plt.show()
