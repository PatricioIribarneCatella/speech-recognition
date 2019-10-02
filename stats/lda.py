import csv
import numpy as np

def main():

    # parse data
    with open('a.txt', 'r') as f:
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

    # mean and sigma calc
    mean_a = np.mean(train_a, axis=0)
    mean_o = np.mean(train_o, axis=0)
    mean_u = np.mean(train_u, axis=0)
    
    sigma_a = np.cov(train_a, rowvar=False)
    sigma_o = np.cov(train_o, rowvar=False)
    sigma_u = np.cov(train_u, rowvar=False)

    sigma = (sigma_a + sigma_o + sigma_u) / 3

    # plot

    

    # function g calc
    # w1
    w1a = mean_a.T * np.inv(sigma)
    w1a = w1a.T
    
    w1o = mean_o.T * np.inv(sigma)
    w1o = w1o.T

    w1u = mean_u.T * np.inv(sigma)
    w1u = w1u.T

    #w0
    w0a = 0.5 * mean_a.T * np.inv(sigma) * mean_a + np.log()

  
if __name__ == "__main__":
    main()

