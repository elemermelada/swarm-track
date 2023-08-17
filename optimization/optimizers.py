from scipy import optimize
import numpy as np

Bounds = optimize.Bounds
minimize = optimize.minimize
ga = optimize.differential_evolution


def TrustRegionOptimizer(f, x0, l_bound, u_bound):
    bounds = Bounds(l_bound, u_bound)
    res = minimize(
        f,
        x0,
        method="trust-constr",
        options={
            "verbose": 3,
            "maxiter": 100,
            "gtol": 0,
        },
        bounds=bounds,
    )
    return res


def SLSQPOptimizer(f, x0, l_bound, u_bound):
    bounds = Bounds(l_bound, u_bound)
    res = minimize(
        f,
        x0,
        method="SLSQP",
        options={"disp": True, "maxiter": 20},
        bounds=bounds,
    )
    return res


def GeneticOptimizer(f, x0, l_bound, u_bound):
    bounds = Bounds(l_bound, u_bound)
    res = ga(
        f,
        bounds,
        disp=True,
        callback=lambda xk, convergence: print("Best:", np.array(xk) * 1e-3),
        popsize=5,  # This is confusing
        # workers=4,
    )
    return res
