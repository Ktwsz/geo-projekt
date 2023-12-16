import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random as rnd

#TODO

fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)


def gen():
    for i in range(3):
        x = rnd.randint(0, 5)
        y = rnd.randint(0, 5)
        print(x, y)

        ax.plot([x], [y], "ro")
        yield ax.get_children()


frames = [x for x in gen()]

ani = animation.ArtistAnimation(fig, frames, interval=500)

ani.save("chuj.gif")
