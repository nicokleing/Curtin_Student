# Student Name : Nicolas Klein
# Student ID   : 21892288

import matplotlib.pyplot as plt
from showground import Pirate

simlength = 10 


pirates = [
    Pirate(50, 30, 20, 30,  frame_color='tab:blue',   accent_color='purple', margin=0.18, vx=6,  vy=0),
    Pirate(105, 10, 40, 50, frame_color='tab:orange', accent_color='green',  margin=0.15, vx=8,  vy=2),
    Pirate(150, 80, 40, 80, frame_color='tab:green',  accent_color='red',    margin=0.22, vx=-10, vy=-1),
]

plt.ion()           
fig = plt.figure()

for t in range(simlength):
    plt.clf()      
    plt.title(f"Showground - Task 4: moving rides (t = {t+1}/{simlength})")  
    plt.xlabel("x"); plt.ylabel("y")


    for p in pirates:
        p.plot_me(plt)
        p.step_change()  

    plt.xlim((0, 200)); plt.ylim((0, 200))
    plt.pause(0.8)  

fig.savefig("task4.png", dpi=150)
plt.ioff()
plt.show()
