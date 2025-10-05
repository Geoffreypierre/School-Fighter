# School Fighter 🥊

Un jeu de combat 2D inspiré de Street Fighter, développé en Python avec Pygame. Incarnez des étudiants dans des combats épiques au sein d'environnements scolaires !

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-required-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 📖 Description

School Fighter est un jeu de combat où des étudiants s'affrontent dans différents décors scolaires (salle de classe, cour de récréation, couloirs, cafétéria). Le jeu propose des animations fluides, des effets sonores immersifs et une IA artisanale pour le mode solo.

## ✨ Fonctionnalités

### Modes de jeu
- **Single Player** : Affrontez une IA contrôlée manuellement (non statistique)
- **Two Players** : Combat local sur le même clavier entre deux joueurs

### Système de combat
- Animations complètes pour chaque action (idle, marche, saut, attaques, défense)
- Attaques spéciales à distance :
  - **Joueur 1** : Boule de feu 🔥
  - **Joueur 2** : Éclair ⚡
- Système de double saut récupérable au sol
- Durée d'attaque ajustée (~1 seconde) pour une meilleure visibilité
- Hitboxes optimisées pour un gameplay équilibré

### Audio
- Effets sonores pour chaque action (coups de poing, coups de pied, attaques spéciales, défense)
- Musique de fond dans les menus
- Contrôle du volume et option de désactivation

### Interface
- Menu principal intuitif
- Écran de paramètres audio
- Instructions de jeu intégrées

## 🎮 Contrôles

### Joueur 1 (Clavier AZERTY)
| Action | Touche |
|--------|--------|
| Déplacement gauche | Q |
| Déplacement droite | D |
| Saut / Double saut | Z |
| Défense | S |
| Coup de poing | F |
| Coup de pied | G |
| Attaque spéciale | H |

### Joueur 2
| Action | Touche |
|--------|--------|
| Déplacement gauche | ← |
| Déplacement droite | → |
| Saut / Double saut | ↑ |
| Défense | ↓ |
| Coup de poing | K |
| Coup de pied | L |
| Attaque spéciale | M |

## 🚀 Installation

### Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/school-fighter.git
cd school-fighter
```

2. Installez les dépendances :
```bash
pip install pygame
```

3. Lancez le jeu :
```bash
python School_fighter1.py
```

## 📁 Structure du projet

```
school-fighter/
│
├── School_fighter1.py      # Fichier principal du jeu
│
├── img/                     # Ressources graphiques
│   ├── backgrounds/
│   │   ├── classroom.jpg
│   │   ├── playground.jpg
│   │   ├── corridors.jpg
│   │   └── cafeteria.jpg
│   ├── sprites/
│   │   ├── player1_*.png
│   │   ├── fireball.png
│   │   └── lightning.png
│
└── sound/                   # Ressources audio
    ├── punch.wav
    ├── kick.wav
    ├── special.wav
    ├── block.wav
    └── background_music.mp3
```

## 🛠️ Développement

### Architecture du code
Le projet suit une architecture de code propre avec séparation des responsabilités :
- **Rendu** : Gestion de l'affichage et des animations
- **Logique** : Mécanique de jeu et détection des collisions
- **Entrées** : Gestion des contrôles joueurs
- **Audio** : Gestion des sons et de la musique

### Technologies utilisées
- **Langage** : Python 3.10+
- **Framework** : Pygame
- **IA** : Algorithme handcrafted (non basé sur des méthodes statistiques)

## 🎯 Méthodologie de développement

Ce projet a été développé en utilisant :
- **Copilot** comme assistant IA pour le développement
- **Prompt Engineering** avec des instructions structurées en JSON
- Architecture de code claire et maintenable
- Environnement virtuel Python pour la gestion des dépendances

## 👥 Auteurs

- **Nadim DOUHANE**
- **Geoffrey PIERRE**

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Forker le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commiter vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Pusher vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 🐛 Bugs connus et améliorations futures

- [ ] Ajouter plus de personnages jouables
- [ ] Implémenter un système de combos
- [ ] Créer un mode tournoi
- [ ] Ajouter des power-ups dans l'arène

## 📧 Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur GitHub.

---

⭐ Si vous aimez ce projet, n'oubliez pas de lui donner une étoile sur GitHub !
