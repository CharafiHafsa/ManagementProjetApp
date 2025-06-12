
import numpy as np
def f_obj(X):
    return 15*X[1]**2*X[0]**2*np.exp(-X[1]**2-X[0]**2)

bornes=[[-10,10],[-10,10]] # l'espace des solutions réalisables

taille_population = 10
population = np.array([
    [np.random.uniform(low, high) for (low, high) in bornes]
    for _ in range(taille_population)
])

print(population)



def ajouter_element_plusieurs_fois(liste, element, nombre_de_fois):
    for _ in range(nombre_de_fois):
        liste.append(element)
    return liste

def selection_davis(population,alpha):
    poids=[]
    Pr=[]
    n=len(population)

    poids=[(n-i)**alpha  for i in range(n)]
    sum_poids=sum(poids)
     
    poids=[n*poids[i]/sum_poids for i in range(n)] 

    
    E=[int(x) for x in Pr]
    nouvelle=[]
    for i in range(n) :
        ajouter_element_plusieurs_fois(nouvelle,,E[i])
        
    

    


