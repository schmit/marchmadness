import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.kernel_regression import KernelReg

def kernelregplot(y, x, xtype='c', jitter=0.0, figsize=(8,5), reg_type='ll'):
    '''
    Creates a scatter plot and including a kernel regression smoothing

    input:
        - y: dependent variable
        - x: independent variable
        - xtype='c': type for x:
            - 'c' for continuous
            - 'u' for unordered
            - 'o' for ordered
        - reg_type='ll': type of regression estimator
            - 'll' for local linear
            - 'lc' for local constant
    '''
    n = len(x)
    assert len(y) == n, 'y and x must have same length'

    # create density estimator
    kr = KernelReg(y, x, xtype, reg_type=reg_type)

    newx = np.linspace(np.min(x), np.max(x))
    newy = kr.fit(newx)[0]

    f, ax = plt.subplots(1, 1, figsize=figsize)

    jit = 2 * jitter * (np.random.random(n) - 0.5)
    ax.plot(x, y + jit, '.')
    ax.plot(newx, newy, 'r')

    return f, ax