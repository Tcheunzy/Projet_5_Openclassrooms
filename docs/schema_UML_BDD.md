# Schéma de la base de données — Projet 5

Ce schéma décrit la structure de la base PostgreSQL utilisée pour enregistrer systématiquement les inputs et outputs du modèle de prédiction du turnover.

## Vue d'ensemble

- **EMPLOYES** : état courant des données RH de chaque employé, identifié par son matricule métier.
- **PREDICTIONS** : historique complet de chaque interaction avec le modèle, avec un instantané figé des données envoyées (traçabilité), lié à un employé via une clé étrangère.
- Relation : un employé peut avoir zéro ou plusieurs prédictions ; chaque prédiction appartient à exactement un employé.

```mermaid
erDiagram
    EMPLOYES ||--o{ PREDICTIONS : "fait l'objet de"

    EMPLOYES{
        int id PK "identifiant technique, auto-incrémenté"
        string matricule UK "identifiant métier fourni par Futurisys"
        int nb_formations_suivies
        int niveau_education
        string domaine_etude
        string frequence_deplacement
        float age
        string genre
        string statut_marital
        string poste
        float annee_experience_totale
        float annees_dans_l_entreprise
        int satisfaction_employee_environnement
        int satisfaction_employee_nature_travail
        int satisfaction_employee_equipe
        int satisfaction_employee_equilibre_pro_perso
        int note_evaluation_actuelle
        int heure_supplementaires
        int augementation_salaire_precedente
        int burnout_score
        int contrainte_mobilite
        float ratio_stagnation_promotion
        float augmentation_vs_perf
        float revenu_par_annee_experience
        float score_satisfaction_global
        int delta_evaluation
        float ratio_experience_entreprises
        float instabilite_carriere
        float engagement_formation
        float epargne_d_entreprise
        timestamp date_maj "date de dernière mise à jour de la fiche employé"

    }

    PREDICTIONS {
        int id PK "identifiant technique, auto-incrémenté"
        int employe_id FK "référence vers EMPLOYES.id"
        timestamp date_prediction "horodatage de la requête"
        jsonb donnees_entree "instantané complet des 28 features envoyées au modèle au moment T"
        float probabilite_depart "sortie brute du modèle (proba de la classe 1)"
        int prediction "0 ou 1, selon le seuil"
        string label "'En poste' ou 'Démission'"
        float seuil_utilise "seuil de décision utilisé (0.40)"
    }
```

## Notes de conception

- "id" (technique) est séparé de "matricule" (métier) pour ne pas coupler la clé primaire à un identifiant qui pourrait évoluer côté client.
- "EMPLOYES" ne conserve que l'état courant (pas de versionnement) : une mise à jour écrase les anciennes valeurs.
- "PREDICTIONS" reste auto-suffisante pour l'audit grâce à la colonne JSON "donnees_entree", qui capture les données exactes envoyées à chaque prédiction, indépendamment de l'évolution ultérieure de "EMPLOYES".
- "probabilite_depart", "prediction", "label", "seuil_utilise" sont des colonnes SQL dédiées (et non dans le JSON) car ce sont les champs les plus susceptibles d'être filtrés/triés/agrégés dans de futures analyses.

