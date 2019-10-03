import csv
import numpy as np
import matplotlib.pyplot as plt

from numpy.linalg import eig
from scipy.linalg import inv

def plot_ellipse(sigma):
    
    # Create ellipses
    d, v = eig(sigma)
    mat = v * inv(np.sqrt(np.diag(d)))

    N = 200
    t = np.arange(0, N) * (2*np.pi) / N

    Y1 = np.sin(t)
    Y2 = np.cos(t)

    X2 = []
    X1 = []

    for y2, y1 in zip(Y2, Y1):
        y = np.array([y2, y1])
        x = mat * y.T
        X2.append(x[0])
        X1.append(x[1])

    fig, ax = plt.subplots()
    fig.suptitle("ellipse for sigma")

    ax.plot(np.array(X2), np.array(X1))
    plt.show()

def plot(samples, means, sigma):

    sam_a = samples["a"]
    sam_o = samples["o"]
    sam_u = samples["u"]

    data = (sam_a.T, sam_o.T, sam_u.T)
    colors = ("red", "green", "blue")
    groups = ("a", "o", "u")

    # Create plot
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    for data, color, group in zip(data, colors, groups):
        x, y = data
        ax.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

    plt.title('A,O,U scatter')
    plt.legend(loc=2)
    plt.show()

def main():

    # parse data
    with open('a.txt') as f:
        lines_a = list(csv.reader(f, delimiter='\t'))

    with open('o.txt') as f:
        lines_o = list(csv.reader(f, delimiter='\t'))

    with open('u.txt') as f:
        lines_u = list(csv.reader(f, delimiter='\t'))

    lines_a = list(map(lambda x: [int(x[0]), int(x[1])],lines_a))
    lines_o = list(map(lambda x: [int(x[0]), int(x[1])],lines_o))
    lines_u = list(map(lambda x: [int(x[0]), int(x[1])],lines_u))

    # separate 'train' and 'test' datasets
    train_a = np.array(lines_a[:49])
    test_a = np.array(lines_a[50:])
    
    train_o = np.array(lines_o[:49])
    test_o = np.array(lines_o[50:])
    
    train_u = np.array(lines_u[:49])
    test_u = np.array(lines_u[50:])

    x_tot = len(train_a) + len(train_o) + len(train_u)

    # mean calc
    mean_a = np.mean(train_a, axis=0)
    mean_o = np.mean(train_o, axis=0)
    mean_u = np.mean(train_u, axis=0)
    
    sigma_a = np.cov(train_a, rowvar=False)
    sigma_o = np.cov(train_o, rowvar=False)
    sigma_u = np.cov(train_u, rowvar=False)

    # sigma calc
    sigma = (sigma_a + sigma_o + sigma_u) / 3

    # plot
    samples = {
        "a": train_a,
        "o": train_o,
        "u": train_u
    }
    mean = {
        "a": mean_a,
        "o": mean_o,
        "u": mean_u
    }
    plot_ellipse(sigma)
    #plot(samples, mean, sigma)

    # w1
    w1a = mean_a.T * inv(sigma)
    w1a = w1a.T
    
    w1o = mean_o.T * inv(sigma)
    w1o = w1o.T

    w1u = mean_u.T * inv(sigma)
    w1u = w1u.T

    # w0
    w0a = 0.5 * mean_a.T * inv(sigma) * mean_a + np.log(len(train_a)/x_tot)
    w0o = 0.5 * mean_o.T * inv(sigma) * mean_o + np.log(len(train_o)/x_tot)
    w0u = 0.5 * mean_u.T * inv(sigma) * mean_u + np.log(len(train_u)/x_tot)

    # function g calc
    ga = lambda x: w1a * x + w0a
    go = lambda x: w1o * x + w0o
    gu = lambda x: w1u * x + w0u     

if __name__ == "__main__":
    main()

