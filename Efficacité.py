import math

def calculate_expression(z):
    # Définir les constantes
    num1 = 1.27e-11
    den1 = math.sqrt(1 + (2.063 * z)**2)
    
    num2 = 8.28e-12
    den2 = 1 + (2.063 * z)**2
    
    term3 = 4.85e-12
    
    # Calcul de l'expression
    numerator = num1 / den1
    denominator = (num2 / den2) + term3
    
    result = (numerator / denominator)**2
    return result

# Exemple d'utilisation avec une valeur de z
z = 0.44

result = calculate_expression(z)
print(f"Le résultat pour z = {z} est : {result:.5e}")
