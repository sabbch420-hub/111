import json
import random
import hashlib
from datetime import datetime
from pymongo import MongoClient  # Requis pour la connexion à MongoDB Atlas

# ==============================================================================
# CONFIGURATION MONGODB ATLAS
# ==============================================================================
MONGO_URI = "mongodb+srv://admin:hadjer2005@smart-building.9v6qqdu.mongodb.net/?appName=smart-building"
DB_NAME = "smart_building"
COLLECTION = "things"

# ==============================================================================
# CARTOGRAPHIE ET COORDONNÉES DES SALLES
# ==============================================================================
FLOOR_MAP = {
    "Observatoire IA":       "Etage 11 - Sky Lab",
    "Salle Drone":           "Etage 11 - Sky Lab",
    "Bureau Innovation":     "Etage 11 - Sky Lab",
    "War Room 11":           "Etage 11 - Sky Lab",
    "Studio XR":             "Etage 11 - Sky Lab",
    "Terrasse Technique":    "Etage 11 - Sky Lab",
    "Direction Produit":     "Etage 10 - Executif",
    "Direction Ops":         "Etage 10 - Executif",
    "Direction Tech":        "Etage 10 - Executif",
    "Board Room":            "Etage 10 - Executif",
    "Lounge 10":             "Etage 10 - Executif",
    "Archives Direction E10":"Etage 10 - Executif",
    "NOC 9A":                "Etage 9 - Data Center",
    "NOC 9B":                "Etage 9 - Data Center",
    "Reseau Core":           "Etage 9 - Data Center",
    "Salle UPS":             "Etage 9 - Data Center",
    "Stock Fibre":           "Etage 9 - Data Center",
    "Monitoring 24-7":       "Etage 9 - Data Center",
    "Lab IoT A":             "Etage 8 - R&D",
    "Lab IoT B":             "Etage 8 - R&D",
    "Prototype Hub":         "Etage 8 - R&D",
    "Test CEM":              "Etage 8 - R&D",
    "QA Hardware":           "Etage 8 - R&D",
    "Atelier R&D":           "Etage 8 - R&D",
    "Classe 7A":             "Etage 7 - Formation",
    "Classe 7B":             "Etage 7 - Formation",
    "Salle Exam":            "Etage 7 - Formation",
    "Media Room":            "Etage 7 - Formation",
    "Cowork 7":              "Etage 7 - Formation",
    "Coaching":              "Etage 7 - Formation",
    "Support N1":            "Etage 6 - Operations",
    "Support N2":            "Etage 6 - Operations",
    "Incident Room":         "Etage 6 - Operations",
    "SRE Hub":               "Etage 6 - Operations",
    "Planning":              "Etage 6 - Operations",
    "Salle Briefing":        "Etage 6 - Operations",
    "Open Space 5A":         "Etage 5 - Collaboration",
    "Open Space 5B":         "Etage 5 - Collaboration",
    "Salle Sprint":          "Etage 5 - Collaboration",
    "Design Studio":         "Etage 5 - Collaboration",
    "Salle Produit":         "Etage 5 - Collaboration",
    "Archives E5":           "Etage 5 - Collaboration",
    "Bureau PDG":            "Etage 4 - Direction",
    "Salle du Conseil":      "Etage 4 - Direction",
    "Salon VIP":             "Etage 4 - Direction",
    "Terrasse Privee":       "Etage 4 - Direction",
    "Secretariat":           "Etage 4 - Direction",
    "Archives Direction E4": "Etage 4 - Direction",
    "Open Space Alpha":      "Etage 3 - Tech",
    "Labo Robotique":        "Etage 3 - Tech",
    "Bureau Lead Dev":       "Etage 3 - Tech",
    "Salle Reunion 3A":      "Etage 3 - Tech",
    "Zone Debug":            "Etage 3 - Tech",
    "Serveurs 3":            "Etage 3 - Tech",
    "Studio Graphique":      "Etage 2 - Marketing",
    "Bureau RH":             "Etage 2 - Marketing",
    "Comptabilite":          "Etage 2 - Marketing",
    "Salle de Presse E2":    "Etage 2 - Marketing",
    "Reunion 2B":            "Etage 2 - Marketing",
    "Bureau Com":            "Etage 2 - Marketing",
    "Archives E2":           "Etage 2 - Marketing",
    "Zone de Stockage":      "Etage 1 - Logistique",
    "Atelier Reparation":    "Etage 1 - Logistique",
    "Local Serveurs":        "Etage 1 - Logistique",
    "Poste Securite":        "Etage 1 - Logistique",
    "Quai d'Expedition":     "Etage 1 - Logistique",
    "Bureau Chef":           "Etage 1 - Logistique",
    "Accueil":               "RDC - Public",
    "Cafeteria":             "RDC - Public",
    "Showroom":              "RDC - Public",
    "Auditorium":            "RDC - Public",
    "Sanitaires":            "RDC - Public",
    "Espace Detente":        "RDC - Public",
}

ROOM_COORDS = {
    "Observatoire IA":       {"x": 10, "y": 230, "z": 44},
    "Salle Drone":           {"x": 20, "y": 230, "z": 44},
    "Bureau Innovation":     {"x": 30, "y": 230, "z": 44},
    "War Room 11":           {"x": 40, "y": 230, "z": 44},
    "Studio XR":             {"x": 50, "y": 230, "z": 44},
    "Terrasse Technique":    {"x": 60, "y": 230, "z": 44},
    "Direction Produit":     {"x": 10, "y": 210, "z": 40},
    "Direction Ops":         {"x": 20, "y": 210, "z": 40},
    "Direction Tech":        {"x": 30, "y": 210, "z": 40},
    "Board Room":            {"x": 40, "y": 210, "z": 40},
    "Lounge 10":             {"x": 50, "y": 210, "z": 40},
    "Archives Direction E10":{"x": 60, "y": 210, "z": 40},
    "NOC 9A":                {"x": 10, "y": 190, "z": 36},
    "NOC 9B":                {"x": 20, "y": 190, "z": 36},
    "Reseau Core":           {"x": 30, "y": 190, "z": 36},
    "Salle UPS":             {"x": 40, "y": 190, "z": 36},
    "Stock Fibre":           {"x": 50, "y": 190, "z": 36},
    "Monitoring 24-7":       {"x": 60, "y": 190, "z": 36},
    "Lab IoT A":             {"x": 10, "y": 170, "z": 32},
    "Lab IoT B":             {"x": 20, "y": 170, "z": 32},
    "Prototype Hub":         {"x": 30, "y": 170, "z": 32},
    "Test CEM":              {"x": 40, "y": 170, "z": 32},
    "QA Hardware":           {"x": 50, "y": 170, "z": 32},
    "Atelier R&D":           {"x": 60, "y": 170, "z": 32},
    "Classe 7A":             {"x": 10, "y": 150, "z": 28},
    "Classe 7B":             {"x": 20, "y": 150, "z": 28},
    "Salle Exam":            {"x": 30, "y": 150, "z": 28},
    "Media Room":            {"x": 40, "y": 150, "z": 28},
    "Cowork 7":              {"x": 50, "y": 150, "z": 28},
    "Coaching":              {"x": 60, "y": 150, "z": 28},
    "Support N1":            {"x": 10, "y": 130, "z": 24},
    "Support N2":            {"x": 20, "y": 130, "z": 24},
    "Incident Room":         {"x": 30, "y": 130, "z": 24},
    "SRE Hub":               {"x": 40, "y": 130, "z": 24},
    "Planning":              {"x": 50, "y": 130, "z": 24},
    "Salle Briefing":        {"x": 60, "y": 130, "z": 24},
    "Open Space 5A":         {"x": 10, "y": 110, "z": 20},
    "Open Space 5B":         {"x": 20, "y": 110, "z": 20},
    "Salle Sprint":          {"x": 30, "y": 110, "z": 20},
    "Design Studio":         {"x": 40, "y": 110, "z": 20},
    "Salle Produit":         {"x": 50, "y": 110, "z": 20},
    "Archives E5":           {"x": 60, "y": 110, "z": 20},
    "Bureau PDG":            {"x": 10, "y": 90,  "z": 16},
    "Salle du Conseil":      {"x": 20, "y": 90,  "z": 16},
    "Salon VIP":             {"x": 30, "y": 90,  "z": 16},
    "Terrasse Privee":       {"x": 40, "y": 90,  "z": 16},
    "Secretariat":           {"x": 50, "y": 90,  "z": 16},
    "Archives Direction E4": {"x": 60, "y": 90,  "z": 16},
    "Open Space Alpha":      {"x": 10, "y": 70,  "z": 12},
    "Labo Robotique":        {"x": 20, "y": 70,  "z": 12},
    "Bureau Lead Dev":       {"x": 30, "y": 70,  "z": 12},
    "Salle Reunion 3A":      {"x": 40, "y": 70,  "z": 12},
    "Zone Debug":            {"x": 50, "y": 70,  "z": 12},
    "Serveurs 3":            {"x": 60, "y": 70,  "z": 12},
    "Studio Graphique":      {"x": 10, "y": 50,  "z": 8},
    "Bureau RH":             {"x": 20, "y": 50,  "z": 8},
    "Comptabilite":          {"x": 30, "y": 50,  "z": 8},
    "Salle de Presse E2":    {"x": 40, "y": 50,  "z": 8},
    "Reunion 2B":            {"x": 50, "y": 50,  "z": 8},
    "Bureau Com":            {"x": 55, "y": 50,  "z": 8},
    "Archives E2":           {"x": 60, "y": 50,  "z": 8},
    "Zone de Stockage":      {"x": 10, "y": 30,  "z": 4},
    "Atelier Reparation":    {"x": 20, "y": 30,  "z": 4},
    "Local Serveurs":        {"x": 30, "y": 30,  "z": 4},
    "Poste Securite":        {"x": 40, "y": 30,  "z": 4},
    "Quai d'Expedition":     {"x": 50, "y": 30,  "z": 4},
    "Bureau Chef":           {"x": 60, "y": 30,  "z": 4},
    "Accueil":               {"x": 10, "y": 10,  "z": 0},
    "Cafeteria":             {"x": 20, "y": 10,  "z": 0},
    "Showroom":              {"x": 30, "y": 10,  "z": 0},
    "Auditorium":            {"x": 40, "y": 10,  "z": 0},
    "Sanitaires":            {"x": 50, "y": 10,  "z": 0},
    "Espace Detente":        {"x": 60, "y": 10,  "z": 0},
}

# ==============================================================================
# DÉFINITION DES 100 OBJETS UNIQUE (NOM, TYPE, EMPlACEMENT, DESCRIPTION)
# ==============================================================================
OBJECTS_DEF = [
    ("Capteur CO2 Observatoire", "Capteur", "Observatoire IA", "Capteur de dioxyde de carbone pour surveiller la qualité de l'air dans l'observatoire IA."),
    ("Caméra Drone Bay", "Camera", "Salle Drone", "Caméra de surveillance haute résolution pour le suivi des drones en vol."),
    ("Écran Interactif Innovation", "Television", "Bureau Innovation", "Écran tactile 4K pour présentations collaboratives et sessions de brainstorming."),
    ("Microphone Conférence War", "Microphone", "War Room 11", "Microphone omnidirectionnel pour capturer les échanges stratégiques."),
    ("Éclairage Scénique XR", "Eclairage", "Studio XR", "Système d'éclairage LED programmable adapté aux tournages XR."),
    ("Capteur Météo Terrasse", "Capteur", "Terrasse Technique", "Station météorologique IoT mesurant température, vent et hygrométrie."),
    ("Haut-parleur Ambiant Sky", "Haut-parleur", "Observatoire IA", "Système audio ambiant diffusant des alertes et de la musique d'ambiance."),
    ("Contrôle Accès Drone Bay", "Controle Acces", "Salle Drone", "Lecteur de badge sécurisé contrôlant l'accès à la salle des drones."),
    ("Interrupteur Ventilation XR", "Interrupteur Connecte", "Studio XR", "Interrupteur connecté pilotant la ventilation du studio XR."),
    ("Climatiseur Direction Produit", "Climatiseur", "Direction Produit", "Climatiseur intelligent avec régulation automatique pour le confort thermique."),
    ("Capteur Présence Board", "Capteur", "Board Room", "Détecteur de présence infrarouge pour la gestion automatique de l'éclairage."),
    ("Caméra Conférence Board", "Camera", "Board Room", "Caméra panoramique 360° pour les visioconférences de direction."),
    ("Haut-parleur Lounge E10", "Haut-parleur", "Lounge 10", "Système audio haute fidélité pour l'ambiance sonore du lounge."),
    ("Éclairage Lounge 10", "Eclairage", "Lounge 10", "Éclairage d'ambiance dimmable pour le lounge exécutif."),
    ("Interrupteur Archives E10", "Interrupteur Connecte", "Archives Direction E10", "Interrupteur connecté pour la gestion de l'éclairage des archives."),
    ("Contrôle Accès Direction", "Controle Acces", "Direction Tech", "Système de contrôle d'accès biométrique sécurisant l'entrée."),
    ("Scanner Documents E10", "Scanner", "Archives Direction E10", "Scanner haute vitesse pour la numérisation de documents confidentiels."),
    ("Capteur Température NOC A", "Capteur", "NOC 9A", "Sonde de température précise pour le centre opérationnel réseau A."),
    ("Capteur Humidité NOC B", "Capteur", "NOC 9B", "Capteur d'humidité relative pour prevenir la condensation."),
    ("Caméra Sécurité Reseau", "Camera", "Reseau Core", "Caméra IP de surveillance 24/7 pour le cœur de réseau."),
    ("Interrupteur UPS Principal", "Interrupteur Connecte", "Salle UPS", "Interrupteur de puissance connecté pour la gestion des onduleurs."),
    ("Capteur Vibration Fibre", "Capteur", "Stock Fibre", "Capteur de vibration pour détecter les manipulations non autorisées."),
    ("Écran Monitoring Central", "Television", "Monitoring 24-7", "Grand écran mural affichant les tableaux de bord de supervision."),
    ("Éclairage Urgence NOC", "Eclairage", "NOC 9A", "Éclairage de secours à LED s'activant lors d'une coupure."),
    ("Contrôle Accès Data Center", "Controle Acces", "Reseau Core", "Portique de sécurité avec double authentification pour l'accès."),
    ("Capteur Qualité Air Lab A", "Capteur", "Lab IoT A", "Analyseur multi-gaz surveillant COV, CO2 et particules fines."),
    ("Caméra Lab IoT B", "Camera", "Lab IoT B", "Caméra de documentation automatique des expériences."),
    ("Imprimante 3D Prototype", "Imprimante", "Prototype Hub", "Imprimante connectée pour le suivi et le lancement d'impressions."),
    ("Capteur CEM Électromagnétique", "Capteur", "Test CEM", "Capteur de compatibilité électromagnétique de précision."),
    ("Scanner QA Hardware", "Scanner", "QA Hardware", "Scanner de codes-barres pour le suivi des composants."),
    ("Climatiseur Atelier R&D", "Climatiseur", "Atelier R&D", "Climatiseur de précision maintenant une température constante."),
    ("Éclairage Technique Lab", "Eclairage", "Lab IoT A", "Éclairage à spectre complet réglable pour travaux de précision."),
    ("Haut-parleur Alerte R&D", "Haut-parleur", "Prototype Hub", "Système d'alerte sonore signalant les étapes critiques."),
    ("Télévision Classe 7A", "Television", "Classe 7A", "Téléviseur interactif 75 pouces pour les cours magistraux."),
    ("Microphone Sans-fil 7B", "Microphone", "Classe 7B", "Microphone HF sans fil permettant aux formateurs de se déplacer."),
    ("Caméra Examen Sécurisée", "Camera", "Salle Exam", "Caméra de surveillance pour garantir l'intégrité des examens."),
    ("Haut-parleur Media Room", "Haut-parleur", "Media Room", "Système audio surround pour les projections multimédias."),
    ("Contrôle Accès Salle Exam", "Controle Acces", "Salle Exam", "Lecteur de badge contrôlant l'accès à la salle d'examen."),
    ("Capteur Présence Coaching", "Capteur", "Coaching", "Capteur de présence pour optimiser l'espace de coaching."),
    ("Climatiseur Cowork 7", "Climatiseur", "Cowork 7", "Climatiseur réversible pour le confort des utilisateurs."),
    ("Interrupteur Projecteur 7A", "Interrupteur Connecte", "Classe 7A", "Interrupteur connecté pour piloter le projecteur à distance."),
    ("Caméra Support N1", "Camera", "Support N1", "Caméra de surveillance de l'espace support niveau 1."),
    ("Capteur Bruit Incident", "Capteur", "Incident Room", "Capteur sonore déclenchant une alerte automatique en cas de bruit."),
    ("Écran Tableau de Bord SRE", "Television", "SRE Hub", "Écran dédié à l'affichage des métriques SRE en continu."),
    ("Imprimante Planning Ops", "Imprimante", "Planning", "Imprimante réseau pour les rapports d'incidents."),
    ("Climatiseur Salle Briefing", "Climatiseur", "Salle Briefing", "Climatiseur compact pour maintenir un environnement confortable."),
    ("Interrupteur Support N2", "Interrupteur Connecte", "Support N2", "Interrupteur connecté gérant l'éclairage de l'espace."),
    ("Bouton Alarme Incident", "Bouton", "Incident Room", "Bouton d'urgence physique connecté déclenchant une alerte."),
    ("Haut-parleur Briefing", "Haut-parleur", "Salle Briefing", "Haut-parleur pour la diffusion des communications d'équipe."),
    ("Capteur CO2 Open 5A", "Capteur", "Open Space 5A", "Capteur de CO2 pour surveiller la qualité de l'air ambiant."),
    ("Télévision Sprint Board", "Television", "Salle Sprint", "Grand écran pour l'affichage du backlog agile."),
    ("Caméra Design Studio", "Camera", "Design Studio", "Caméra pour l'enregistrement des sessions de design thinking."),
    ("Imprimante Design", "Imprimante", "Design Studio", "Imprimante couleur grand format pour supports visuels."),
    ("Climatiseur Open 5B", "Climatiseur", "Open Space 5B", "Climatiseur multi-split pour le confort de l'open space."),
    ("Contrôle Accès Archives E5", "Controle Acces", "Archives E5", "Système de contrôle d'accès sécurisant les archives."),
    ("Bouton Appel Salle Produit", "Bouton", "Salle Produit", "Bouton connecté permettant de signaler l'état de la salle."),
    ("Haut-parleur Open 5A", "Haut-parleur", "Open Space 5A", "Système de sonorisation de l'open space 5A."),
    ("Caméra Sécurité PDG", "Camera", "Bureau PDG", "Caméra discrète de haute sécurité protégeant le bureau du PDG."),
    ("Interrupteur Salon VIP", "Interrupteur Connecte", "Salon VIP", "Interrupteur connecté contrôlant l'éclairage du salon VIP."),
    ("Capteur Présence Secrétariat", "Capteur", "Secretariat", "Capteur de présence pour déclencher automatiquement l'éclairage."),
    ("Climatiseur Salle Conseil", "Climatiseur", "Salle du Conseil", "Climatiseur silencieux pour garantir le confort en réunion."),
    ("Scanner Archives E4", "Scanner", "Archives Direction E4", "Scanner haute résolution pour documents confidentiels."),
    ("Éclairage Terrasse Privée", "Eclairage", "Terrasse Privee", "Éclairage extérieur LED avec détection de présence."),
    ("Haut-parleur Salon VIP", "Haut-parleur", "Salon VIP", "Système audio premium pour la diffusion sonore."),
    ("Bouton Urgence Bureau PDG", "Bouton", "Bureau PDG", "Bouton d'alerte silencieuse relié au poste de sécurité."),
    ("Caméra Open Space Alpha", "Camera", "Open Space Alpha", "Caméra de surveillance de l'open space tech."),
    ("Capteur Présence Labo Robot", "Capteur", "Labo Robotique", "Capteur de présence et de mouvement pour la sécurité du labo."),
    ("Imprimante Lead Dev", "Imprimante", "Bureau Lead Dev", "Imprimante laser réseau pour les documentations techniques."),
    ("Éclairage Zone Debug", "Eclairage", "Zone Debug", "Éclairage intense réglable pour les sessions de débogage."),
    ("Climatiseur Serveurs 3", "Climatiseur", "Serveurs 3", "Climatiseur de précision pour maintenir la température stable."),
    ("Contrôle Accès Serveurs 3", "Controle Acces", "Serveurs 3", "Système d'accès restreint à double facteur."),
    ("Bouton Déploiement Rapide", "Bouton", "Bureau Lead Dev", "Bouton physique connecté déclenchant le pipeline."),
    ("Scanner Inventaire Tech", "Scanner", "Open Space Alpha", "Scanner portable connecté pour l'inventaire matériel."),
    ("Caméra Studio Graphique", "Camera", "Studio Graphique", "Caméra de documentation des créations graphiques."),
    ("Imprimante RH", "Imprimante", "Bureau RH", "Imprimante multifonction pour les documents administratifs."),
    ("Scanner Comptabilité", "Scanner", "Comptabilite", "Scanner de documents comptables pour dématérialisation."),
    ("Microphone Presse", "Microphone", "Salle de Presse E2", "Microphone de conférence de presse haute fidélité."),
    ("Caméra Conférence Presse", "Camera", "Salle de Presse E2", "Caméra de diffusion pour les communications en direct."),
    ("Haut-parleur Réunion 2B", "Haut-parleur", "Reunion 2B", "Système audio de salle pour les visioconférences."),
    ("Éclairage Studio Graph", "Eclairage", "Studio Graphique", "Éclairage professionnel à spectre naturel."),
    ("Interrupteur Bureau Com", "Interrupteur Connecte", "Bureau Com", "Interrupteur connecté pour la gestion énergétique."),
    ("Caméra Quai Expédition", "Camera", "Quai d'Expedition", "Caméra extérieure pour la surveillance des livraisons."),
    ("Scanner Code-barres Stockage", "Scanner", "Zone de Stockage", "Scanner industriel de codes-barres pour le stock."),
    ("Capteur Fumée Atelier", "Capteur", "Atelier Reparation", "Détecteur de fumée et de chaleur pour la sécurité incendie."),
    ("Contrôle Accès Serveurs 1", "Controle Acces", "Local Serveurs", "Contrôle d'accès sécurisé avec journal des entrées."),
    ("Interrupteur Éclairage Quai", "Interrupteur Connecte", "Quai d'Expedition", "Interrupteur industriel connecté pilotant les projecteurs."),
    ("Caméra Poste Sécurité", "Camera", "Poste Securite", "Caméra centrale du poste de sécurité."),
    ("Éclairage Urgence Atelier", "Eclairage", "Atelier Reparation", "Éclairage de secours à batterie pour l'atelier."),
    ("Bouton Appel Chef Log", "Bouton", "Bureau Chef", "Bouton connecté permettant de convoquer l'équipe."),
    ("Machine à Café Accueil", "Machine a Cafe", "Accueil", "Machine à café connectée en libre-service."),
    ("Caméra Entrée Principale", "Camera", "Accueil", "Caméra de sécurité de l'accès principal."),
    ("Télévision Showroom", "Television", "Showroom", "Écran de présentation 85 pouces pour la diffusion."),
    ("Haut-parleur Auditorium", "Haut-parleur", "Auditorium", "Système audio professionnel multi-canal."),
    ("Éclairage Scène Auditorium", "Eclairage", "Auditorium", "Éclairage de scène programmable à LED."),
    ("Capteur Affluence Cafétéria", "Capteur", "Cafeteria", "Capteur de comptage de personnes pour l'affluence."),
    ("Climatiseur Espace Détente", "Climatiseur", "Espace Detente", "Climatiseur réversible pour l'espace détente."),
    ("Contrôle Accès Principal", "Controle Acces", "Accueil", "Portique de contrôle d'accès principal."),
    ("Bouton Appel Réception", "Bouton", "Accueil", "Bouton d'appel connecté pour les visiteurs."),
    ("Interrupteur Showroom", "Interrupteur Connecte", "Showroom", "Interrupteur connecté pour scènes lumineuses."),
    ("Écran Synthèse Ops", "Television", "Support N1", "Écran mural affichant la synthèse globale des indicateurs."),
    ("Capteur Luminosité Alpha", "Capteur", "Open Space Alpha", "Capteur de luminosité ambiante adaptatif."),
    ("Haut-parleur Lab IoT B", "Haut-parleur", "Lab IoT B", "Diffuseur de notifications sonores de test."),
    ("Interrupteur Cafétéria", "Interrupteur Connecte", "Cafeteria", "Interrupteur connecté pour planification de l'éclairage."),
    ("Microphone Direction", "Microphone", "Salle du Conseil", "Microphone de table haute sensibilité pour conseils.")
]

# ==============================================================================
# CONFIGURATIONS SÉMANTIQUES PAR TYPE DE DISPOSITIF IoT
# ==============================================================================
TYPE_CONFIG = {
    "Bouton": {
        "wot_type": "button",
        "category": "Bouton",
        "td_actions": ["press", "release"],
        "control_actions": [
            {"name": "press",   "method": "POST", "action_type": "ActivateAction"},
            {"name": "release", "method": "POST", "action_type": "DeactivateAction"},
        ],
        "device_state": {"power": "off", "last_action": None},
        "properties": ["status"],
        "events": [],
    },
    "Camera": {
        "wot_type": "camera",
        "category": "Camera",
        "td_actions": ["startRecording", "stopRecording", "snapshot"],
        "control_actions": [
            {"name": "startRecording", "method": "POST", "action_type": "ActivateAction"},
            {"name": "stopRecording",  "method": "POST", "action_type": "DeactivateAction"},
            {"name": "snapshot",       "method": "POST", "action_type": "Action"},
            {"name": "status",         "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "off", "recording": False, "motion": False},
        "properties": ["status"],
        "events": [],
    },
    "Capteur": {
        "wot_type": "sensor",
        "category": "Capteur",
        "td_actions": ["reset", "calibrate"],
        "control_actions": [
            {"name": "reset",     "method": "POST", "action_type": "Action"},
            {"name": "calibrate", "method": "POST", "action_type": "Action"},
            {"name": "status",    "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "on", "temperature": 22.0, "humidity": 45.0},
        "properties": ["status"],
        "events": [],
    },
    "Climatiseur": {
        "wot_type": "hvac",
        "category": "Climatiseur",
        "td_actions": ["on", "off", "setTemp", "setMode"],
        "control_actions": [
            {"name": "on",      "method": "POST", "action_type": "ActivateAction"},
            {"name": "off",     "method": "POST", "action_type": "DeactivateAction"},
            {"name": "setTemp", "method": "POST", "action_type": "Action"},
            {"name": "setMode", "method": "POST", "action_type": "Action"},
            {"name": "status",  "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "off", "mode": "cool", "targetTemp": 22},
        "properties": ["status"],
        "events": [],
    },
    "Controle Acces": {
        "wot_type": "access_control",
        "category": "Controle Acces",
        "td_actions": ["lock", "unlock", "grant"],
        "control_actions": [
            {"name": "lock",   "method": "POST", "action_type": "Action"},
            {"name": "unlock", "method": "POST", "action_type": "Action"},
            {"name": "grant",  "method": "POST", "action_type": "Action"},
            {"name": "status", "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "on", "locked": True, "last_badge": None},
        "properties": ["status"],
        "events": [],
    },
    "Eclairage": {
        "wot_type": "light",
        "category": "Éclairage",
        "td_actions": ["on", "off", "setBrightness"],
        "control_actions": [
            {"name": "on",            "method": "POST", "action_type": "ActivateAction"},
            {"name": "off",           "method": "POST", "action_type": "DeactivateAction"},
            {"name": "setBrightness", "method": "POST", "action_type": "Action"},
            {"name": "status",        "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "off", "brightness": 100, "color": "#FFFFFF"},
        "properties": ["status"],
        "events": [],
    },
    "Haut-parleur": {
        "wot_type": "speaker",
        "category": "Haut-parleur",
        "td_actions": ["play", "stop", "setVolume", "mute"],
        "control_actions": [
            {"name": "play",      "method": "POST", "action_type": "ActivateAction"},
            {"name": "stop",      "method": "POST", "action_type": "DeactivateAction"},
            {"name": "setVolume", "method": "POST", "action_type": "Action"},
            {"name": "mute",      "method": "POST", "action_type": "Action"},
            {"name": "status",    "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "off", "volume": 50, "muted": False},
        "properties": ["status"],
        "events": [],
    },
    "Imprimante": {
        "wot_type": "printer",
        "category": "Imprimante",
        "td_actions": ["on", "off", "printTestPage"],
        "control_actions": [
            {"name": "on",            "method": "POST", "action_type": "ActivateAction"},
            {"name": "off",           "method": "POST", "action_type": "DeactivateAction"},
            {"name": "printTestPage", "method": "POST", "action_type": "Action"},
            {"name": "status",        "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "off", "last_action": None},
        "properties": ["status"],
        "events": [],
    },
    "Interrupteur Connecte": {
        "wot_type": "switch",
        "category": "Interrupteur Connecte",
        "td_actions": ["on", "off", "toggle"],
        "control_actions": [
            {"name": "on",     "method": "POST", "action_type": "ActivateAction"},
            {"name": "off",    "method": "POST", "action_type": "DeactivateAction"},
            {"name": "toggle", "method": "POST", "action_type": "Action"},
            {"name": "status", "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "off", "last_action": None},
        "properties": ["status"],
        "events": [],
    },
    "Machine a Cafe": {
        "wot_type": "coffee",
        "category": "Machine a Cafe",
        "td_actions": ["brewCoffee", "stopCoffee", "clean"],
        "control_actions": [
            {"name": "brewCoffee", "method": "POST", "action_type": "ActivateAction"},
            {"name": "stopCoffee", "method": "POST", "action_type": "DeactivateAction"},
            {"name": "clean",      "method": "POST", "action_type": "Action"},
            {"name": "status",     "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "off", "last_action": None},
        "properties": ["status"],
        "events": [],
    },
    "Microphone": {
        "wot_type": "microphone",
        "category": "Microphone",
        "td_actions": ["mute", "unmute", "record"],
        "control_actions": [
            {"name": "mute",   "method": "POST", "action_type": "Action"},
            {"name": "unmute", "method": "POST", "action_type": "Action"},
            {"name": "record", "method": "POST", "action_type": "ActivateAction"},
            {"name": "status", "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "on", "muted": True, "recording": False},
        "properties": ["status"],
        "events": [],
    },
    "Scanner": {
        "wot_type": "scanner",
        "category": "Scanner",
        "td_actions": ["on", "off", "scan"],
        "control_actions": [
            {"name": "on",     "method": "POST", "action_type": "ActivateAction"},
            {"name": "off",    "method": "POST", "action_type": "DeactivateAction"},
            {"name": "scan",   "method": "POST", "action_type": "Action"},
            {"name": "status", "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "off", "last_action": None},
        "properties": ["status"],
        "events": [],
    },
    "Television": {
        "wot_type": "tv",
        "category": "Television",
        "td_actions": ["powerOn", "powerOff", "setVolume", "setChannel"],
        "control_actions": [
            {"name": "powerOn",    "method": "POST", "action_type": "ActivateAction"},
            {"name": "powerOff",   "method": "POST", "action_type": "DeactivateAction"},
            {"name": "setVolume",  "method": "POST", "action_type": "Action"},
            {"name": "setChannel", "method": "POST", "action_type": "Action"},
            {"name": "status",     "method": "GET",  "action_type": None},
        ],
        "device_state": {"power": "off", "volume": 30, "channel": 1},
        "properties": ["status"],
        "events": [],
    },
}

# ==============================================================================
# UTILITAIRES DE GÉNÉRATION SÉQUENTIELLE ET ALGORITHMES
# ==============================================================================
def make_id(name: str, idx: int) -> str:
    raw = f"{name}_{idx}_{random.randint(10000,99999)}"
    return hashlib.md5(raw.encode()).hexdigest()[:8]

def make_search_name(name: str) -> str:
    import unicodedata
    n = name.lower().strip()
    n = unicodedata.normalize("NFD", n)
    n = "".join(ch for ch in n if unicodedata.category(ch) != "Mn")
    n = n.replace(" ", "_").replace("-", "_").replace("'", "").replace("é","e").replace("è","e").replace("ê","e").replace("à","a").replace("ô","o")
    return n

NOW = "2026-05-19T10:00:00.000000Z"
STATE_NOW = "2026-05-19T09:30:00.000000+00:00"

random.seed(42)
docs = []

# ==============================================================================
# BOUCLE DE COMPOSITION DES OBJETS SÉMANTIQUES WoT
# ==============================================================================
for idx, (name, obj_type, room, description) in enumerate(OBJECTS_DEF):
    oid = make_id(name, idx)
    cfg = TYPE_CONFIG[obj_type]
    coords = ROOM_COORDS[room]
    floor = FLOOR_MAP[room]
    search_name = make_search_name(name)
    wot_type = cfg["wot_type"]
    wot_id = f"urn:dev:wot:intellibuild:{oid}"
    gw_base = "https://wot-gateway.example.com"
    
    # 1. Construction dynamique de l'objet actions (Thing Description)
    td_actions_obj = {}
    for ca in cfg["control_actions"]:
        if ca["method"] == "GET":
            continue
        if ca["action_type"] == "ActivateAction":
            desc = f"Activer {name}"
        elif ca["action_type"] == "DeactivateAction":
            desc = f"Désactiver {name}"
        else:
            desc = f"Action {ca['name']} sur {name}"
            
        td_actions_obj[ca["name"]] = {
            "description": desc,
            "forms": [{
                "href": f"{gw_base}/{wot_type}/{oid}/{ca['name']}",
                "op": "invokeaction",
                "htv:methodName": "POST",
                "contentType": "application/json"
            }]
        }
        
    # 2. Construction de la liste des control actions (Schema.org / WoT Bridge)
    control_actions_list = []
    for ca in cfg["control_actions"]:
        entry = {
            "name": ca["name"],
            "method": ca["method"],
            "href": f"{gw_base}/{wot_type}/{oid}/{ca['name']}" if ca["method"] == "POST" else f"{gw_base}/{oid}/properties/status",
        }
        if ca["action_type"]:
            entry["potentialAction"] = {"@type": ca["action_type"]}
        control_actions_list.append(entry)
        
    # 3. Actions potentielles (potentialAction)
    potential_actions = []
    for ca in cfg["control_actions"]:
        if ca["action_type"]:
            potential_actions.append({
                "@type": ca["action_type"],
                "name": ca["name"],
                "target": f"{gw_base}/{wot_type}/{oid}/{ca['name']}"
            })
            
    # MODIFICATION EFFECTUÉE : Uniquement disponible et indisponible (80% dispo / 20% indispo)
    statuses = ["disponible", "disponible", "disponible", "disponible", "indisponible"]
    status = statuses[idx % len(statuses)]
    
    # Structure de document final optimisée pour MongoDB
    doc = {
        "_id": oid, # Utilisation de l'ID MD5 court comme clé principale MongoDB
        "@context": "https://schema.org",
        "@type": "Product",
        "id": oid,
        "name": name,
        "search_name_norm": search_name,
        "type": cfg["category"],
        "description": description,
        "status": status,
        "location": {
            "@type": "Place",
            "name": room,
            "room": room,
            "floor": floor,
            "x": coords["x"],
            "y": coords["y"],
            "z": coords["z"],
        },
        "view_count": random.randint(1, 20),
        "maintenance_state": "",
        "td_summary": {
            "td_id": wot_id,
            "wot_id": wot_id,
            "title": name,
            "name": name,
            "type": wot_type,
            "description": f"Dispositif IoT sémantique de type {wot_type}",
            "actions": cfg["td_actions"],
            "properties": cfg["properties"],
            "events": cfg["events"],
        },
        "source": "gateway_migration",
        "source_url": f"{gw_base}/td/{oid}",
        "retrieved_at": NOW,
        "thingDescription": {
            "@context": [
                "https://www.w3.org/2022/wot/td/v1.1",
                "https://schema.org/"
            ],
            "@type": "Thing",
            "id": wot_id,
            "title": name,
            "name": name,
            "description": f"Dispositif IoT sémantique de type {wot_type}",
            "category": cfg["category"],
            "properties": {
                "status": {
                    "description": "Current status",
                    "type": "string",
                    "readOnly": True,
                    "forms": [{
                        "href": f"{gw_base}/{oid}/properties/status",
                        "op": "readproperty",
                        "contentType": "application/json"
                    }]
                }
            },
            "actions": td_actions_obj,
            "events": {}
        },
        "device_state": {
            **cfg["device_state"],
            "last_action_at": STATE_NOW,
            "reachable": True
        },
        "control_actions": control_actions_list,
        "potentialAction": potential_actions,
    }
    docs.append(doc)

# ==============================================================================
# VALIDATION FINALE ET ENVOI DIRECT SUR MONGO DB ATLAS
# ==============================================================================
print("⏳ Tentative de connexion à MongoDB Atlas...")
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    col = db[COLLECTION]
    
    # Nettoyer l'ancienne collection si tu veux écraser les anciennes données de test (optionnel)
    # col.delete_many({})
    
    print(f"⏳ Insertion en bloc de {len(docs)} objets IoT...")
    result = col.insert_many(docs)
    
    print("==================================================================")
    print(f"✅ FINISHED WITH SUCCESS !")
    print(f"   -> {len(result.inserted_ids)} documents insérés avec succès.")
    print(f"   -> Collection ciblée : '{DB_NAME}.{COLLECTION}'")
    print("==================================================================")

except Exception as e:
    print(f"❌ Une erreur est survenue lors de l'injection : {e}")