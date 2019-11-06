import numpy as np
from matplotlib import pyplot as plt

def plot(X, Y, kwargs):

    title = None
    name = None
    xlabel = None
    ylabel = None
    show = False

    if "title" in kwargs:
        title = kwargs["title"]
    if "name" in kwargs:
        name = kwargs["name"]
    if "xlabel" in kwargs:
        xlabel = kwargs["xlabel"]
    if "ylabel" in kwargs:
        ylabel = kwargs["ylabel"]
    if "show" in kwargs:
        show = kwargs["show"]

    fig, ax = plt.subplots()
    
    fig.suptitle(title)
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.plot(X, Y)
    
    if show:
        plt.show()
    else:
        plt.savefig("{}.svg".format(name))

def plot_xtrogram(t, f, Sxx, Fs, kwargs):

    show = False
    title = None
    name = None

    if "show" in kwargs:
        show = kwargs["show"]
    if "title" in kwargs:
        title = kwargs["title"]
    if "name" in kwargs:
        name = kwargs["name"]

    fig, ax = plt.subplots()

    fig.suptitle(title)
    ax.pcolormesh(t, f, np.log(np.abs(Sxx)))
    ax.set(xlabel='Time [s]', ylabel='Frequecy [Hz]')
    ax.set_ylim(0, Fs/2)
    ax.plot()
    
    if show:
        plt.show()
    else:
        plt.savefig("{}.png".format(name))

