import warnings
# On coupe définitivement le bruit inutile
warnings.filterwarnings("ignore")

from qiskit.primitives import StatevectorSampler #type: ignore
from qiskit import transpile #type: ignore
from qiskit_algorithms import QAOA #type: ignore
from qiskit_algorithms.optimizers import COBYLA #type: ignore
from qiskit_optimization.algorithms import MinimumEigenOptimizer #type: ignore

# --- LE BOUCLIER ANTI-FREEZE ---
class FastSampler(StatevectorSampler):
    def __init__(self, **kwargs):
        # On fixe 1024 tirs pour éviter un calcul infini
        super().__init__(default_shots=1024, **kwargs)

    def run(self, pubs, *, shots=None):
        new_pubs = []
        for pub in pubs:
            try:
                # Qiskit envoie souvent les données sous forme de Tuple V2
                if isinstance(pub, tuple):
                    circuit = pub[0]
                    # LA MAGIE : On casse le gros bloc QAOA en petites portes super rapides
                    fast_circ = transpile(circuit, basis_gates=['rz', 'sx', 'x', 'cx'])
                    new_pubs.append((fast_circ,) + pub[1:])
                
                # S'il envoie un objet Pub complexe
                elif hasattr(pub, 'circuit'):
                    fast_circ = transpile(pub.circuit, basis_gates=['rz', 'sx', 'x', 'cx'])
                    params = getattr(pub, 'parameter_values', [])
                    new_pubs.append((fast_circ, params))
                
                # Fallback standard
                else:
                    fast_circ = transpile(pub, basis_gates=['rz', 'sx', 'x', 'cx'])
                    new_pubs.append(fast_circ)
            except Exception:
                # Si format inconnu, on laisse passer
                new_pubs.append(pub)
                
        return super().run(new_pubs, shots=shots)


def resoudre_sur_aer(qubo_problem, reps=1, maxiter=70):
    # 1. On utilise notre simulateur optimisé
    simulateur = FastSampler()
    
    # 2. L'optimiseur (20 itérations c'est bien pour QAOA)
    optimiseur = COBYLA(maxiter=maxiter)
    
    # 3. La configuration QAOA (reps=1 pour commencer doucement)
    qaoa = QAOA(sampler=simulateur, optimizer=optimiseur, reps=reps)
    
    # 4. Le solveur avec pénalité
    qaoa_optimizer = MinimumEigenOptimizer(qaoa, penalty=50.0)
    
    # 5. Calcul
    resultat = qaoa_optimizer.solve(qubo_problem)
    
    return resultat