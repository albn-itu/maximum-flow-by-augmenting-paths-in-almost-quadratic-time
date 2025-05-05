import math

base_n = 10
c_6_5 = 1
kappa = 1
phi = 0.2

for i in range(2, 400):
    n: int = base_n**i
    eta = math.log(n)
    h = math.ceil(((4 * (eta**4) * c_6_5 * (math.log(n) ** 7) * kappa) / (phi**2)) * n)

    print(f"n: {base_n}^{i}, h: {h}")
    if h < n:
        print("smaller")
        break
