import numpy as np

def gradient_descent(a, b, c, d, learning_rate=0.01, epochs=1000):
    
    x = np.random.rand() # Starting from a random point ensures you don’t get stuck in a biased location.
    for _ in range(epochs): 
        fx = a*x**3 + b*x**2 + c*x + d   # calculate f(x) 
        dfx = 3*a*x**2 + 2*b*x + c   # calculate derivative of f(x)

        if dfx == 0:
            print("Oops! Derivative is zero. Cannot continue.")
            return None
          
        x = x - learning_rate * (fx / dfx)  # Update x using the (Newton-Raphson formula w/ Learning Rate) ==> Gradient Descent
    return x

    """
      1. fx = How wrong we are (how far from zero).
      2. dfx = How fast fx is changing (slope).
      3. fx / dfx = How much we should adjust x to reduce fx.
      4. learning_rate = Control how big the adjustment is.
      5. x = x - learning_rate * (fx / dfx) = Take a step towards the root.
    """

try:
    a = float(input("Enter the coefficient a (for x^3): "))
    b = float(input("Enter the coefficient b (for x^2): "))
    c = float(input("Enter the coefficient c (for x): "))
    d = float(input("Enter the constant term d: "))
    learning_rate = float(input("Enter the learning rate: "))
    epochs = int(input("Enter the number of epochs (iterations): "))

    root = gradient_descent(a, b, c, d, learning_rate, epochs)

    print(f"\nThe equation is: {a}x^3 + {b}x^2 + {c}x + {d} = 0")
    print(f"Solution for x = {root:.4f}")


except ValueError:
    print("Please enter valid numerical values.")