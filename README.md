# 🚀 Convertisseur Ventes vers Sage (Automatisation Comptable)

Application web développée sous Django permettant d'automatiser la conversion d'exports de ventes bruts (Excel, CSV) en écritures comptables formatées pour le logiciel Sage. 

## ✨ Fonctionnalités Principales
* **Traitement par lot :** Importation simultanée de plusieurs fichiers de ventes via une interface web fluide.
* **Logique Comptable Automatisée :** Attribution intelligente des comptes de ventes (ex: 707000, 707910, 707930) en fonction du pays de l'acheteur (France, UE, Export).
* **Détection des Paiements :** Routage automatique vers les comptes spécifiques (411CB, 411VIR, 411FAI) selon le mode de règlement détecté dans le fichier source.
* **Export Flexible :** Génération des fichiers finaux compatibles Sage au format Excel (`.xlsx`), Texte (`.csv`), ou regroupés dynamiquement dans une archive (`.zip`).

## ⚠️ Avertissement : Reconnaissance Client Personnalisée
Ce code intègre une fonction de reconnaissance par dictionnaire (`MAPPING_SARL_MOMENT` dans le fichier `views.py`) qui détecte des acheteurs récurrents pour leur attribuer un compte VIP (ex: 411TUR). 
**Ces noms et codes sont spécifiques à un cas d'usage précis et servent d'exemple.** Si vous clonez ce projet pour votre propre gestion, vous devrez adapter ce dictionnaire dans le code avec vos propres clients, ou simplement utiliser le mode de conversion "Standard (Auto)" depuis l'interface web.

## 🔄 Évolution du Projet
Ce projet est un outil vivant, en cours d'amélioration continue. Le code sera mis à jour au fur et à mesure pour optimiser les performances et ajouter de nouveaux modules. 
*En cours de développement : Un utilitaire d'extraction OCR/Regex pour traiter directement des factures au format PDF complexe.*

## 🌍 Démo en direct
Testez l'application directement ici : [**Convertisseur Sage - Live**](https://convert-sage-app.onrender.com)

> ⏳ *Note : L'application étant hébergée sur un serveur gratuit, elle se met en veille en cas d'inactivité. Le tout premier chargement peut donc prendre environ 50 secondes pour se réveiller. Les actions suivantes seront instantanées !*

## 🛠️ Installation & Lancement Rapide
1. Clonez ce dépôt sur votre machine locale : 
   `https://github.com/m3hdi-sys/Convert_Sage.git`
2. Placez-vous dans le dossier du projet : 
   `cd Convert_Sage`
3. Créez un environnement virtuel isolé : 
   `python -m venv venv`
4. Activez l'environnement virtuel :
   * Sur Windows : `venv\Scripts\activate`
   * Sur Mac/Linux : `source venv/bin/activate`
5. Installez les dépendances requises : 
   `pip install -r requirements.txt`
6. Lancez le serveur local Django : 
   `python manage.py runserver`
7. Ouvrez votre navigateur sur l'adresse indiquée (généralement `http://127.0.0.1:8000`).
