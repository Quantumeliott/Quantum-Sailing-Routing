import random

def afficher_enigme():
    liste_enigmes = [
        ("Qu'est-ce qui a des clés mais ne peut pas ouvrir de serrures ?", "Un clavier"),
        ("Plus j'en ai, moins on voit. Qui suis-je ?", "L'obscurité"),
        ("Je ne respire jamais mais j'ai besoin d'air. Qui suis-je ?", "Le feu"),
        ("Qu'est-ce qui appartient à l'informaticien mais que les autres utilisent plus que lui ?", "Son nom"),
        ("Je commence par 'e', je finis par 'e', et je ne contiens qu'une seule lettre. Qui suis-je ?", "Une enveloppe"),
        ("Si vous m'avez, vous voulez me partager. Si vous me partagez, vous ne m'avez plus.", "Un secret"),
        ("Quel mot devient plus court quand on lui ajoute deux lettres ?", "Court"),
        ("Je suis toujours là-bas, mais je n'arrive jamais. Qui suis-je ?", "Demain"),
        ("Qu'est-ce qui monte et descend mais reste toujours à la même place ?", "L'escalier"),
        ("On me trouve une fois dans une minute, deux fois dans un moment, mais jamais dans un siècle.", "La lettre M"),
        ("Plus on en retire, plus je deviens grand. Qui suis-je ?", "Un trou"),
        ("Je peux voyager dans le monde entier tout en restant dans mon coin.", "Un timbre"),
        ("Qu'est-ce qui a un œil mais ne voit rien ?", "Une aiguille"),
        ("Quel est le point commun entre un développeur et un boulanger ?", "Ils ont tous les deux besoin de 'pâte' (path)"),
        ("Je ne marche pas, mais j'ai des pieds. Qui suis-je ?", "Un lit"),
        ("Qu'est-ce qui est plein de trous mais retient l'eau ?", "Une éponge"),
        ("Je ne parle pas, mais je réponds quand on m'appelle.", "L'écho"),
        ("Quelle invention permet de regarder à travers les murs ?", "La fenêtre"),
        ("Qu'est-ce qui court mais n'a pas de jambes ?", "L'eau (ou une rivière)"),
        ("Je peux être cassé sans être touché. Qui suis-je ?", "Une promesse")
    ]
    
    enigme, reponse = random.choice(liste_enigmes)
    print(f"Énigme pour vous faire patienter: {enigme}")
    return reponse
