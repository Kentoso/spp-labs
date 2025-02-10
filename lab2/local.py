import random
import math
import time


class MonteCarloIntegrator:
    def __init__(self, func):
        self.func = func

    def integrate(self, a, b, num_samples):
        total = 0.0
        for _ in range(num_samples):
            x = a + (b - a) * random.random()
            total += self.func(x)

        average_value = total / num_samples
        integral_estimate = (b - a) * average_value
        return integral_estimate


if __name__ == "__main__":

    def f(x):
        return math.sqrt(1 - x**2)

    integrator = MonteCarloIntegrator(f)

    start = time.perf_counter_ns()
    result = integrator.integrate(0, 1, num_samples=1000000000)
    end = time.perf_counter_ns()

    print("Time taken:", (end - start) / 1e9)
    print("Estimated integral from 0 to 1:", result * 4)
