# Fiche technique du modèle — Prédiction du turnover

## Objectif métier

Prédire si un employé de Futurisys va quitter volontairement l'entreprise,
à partir de 28 variables RH (satisfaction, ancienneté, évaluation, situation
personnelle, etc.), afin de permettre des actions RH préventives ciblées.

## Origine

Modèle développé lors du **Projet 4** de la formation (notebook
`notebooks/Projet_4_PELLETER_Cheun.ipynb`), réutilisé et industrialisé dans
ce Projet 5.

## Données d'entraînement

- Source : 3 fichiers CSV fusionnés (évaluations, SIRH, sondage de satisfaction)
- Target : `target_binaire` (1 = a démissionné, 0 = toujours en poste)
- 28 features en entrée : 23 numériques, 1 ordinale (`frequence_deplacement`),
  4 nominales (`genre`, `statut_marital`, `poste`, `domaine_etude`)

## Preprocessing

`ColumnTransformer` scikit-learn :

| Type de colonnes | Traitement |
|---|---|
| Numériques | `SimpleImputer(median)` + `StandardScaler` |
| Ordinale (`frequence_deplacement`) | `SimpleImputer(most_frequent)` + `OrdinalEncoder` |
| Nominales | `SimpleImputer(most_frequent)` + `OneHotEncoder` |

## Gestion du déséquilibre de classes

`SMOTETomek` appliqué **uniquement pendant l'entraînement**, sur les données
d'entraînement. N'intervient jamais lors de l'inférence — le pipeline déployé
ne fait que du `predict_proba` sur le modèle déjà entraîné.

## Modèles comparés

| Modèle | Recall | Remarque |
|---|---|---|
| Dummy Classifier | — | Référence de base |
| **LogisticRegression** ✅ | **0.73** | **Retenu** — meilleur recall, interprétable, SHAP réalisé dessus |
| SVM | — | Comparé, non retenu |
| RandomForest | — | Comparé, non retenu |
| CatBoost | — | Comparé, non retenu (recall inférieur malgré une F1 parfois meilleure) |
| LightGBM | — | Comparé, non retenu |
| XGBoost | — | Comparé, non retenu |

Recherche d'hyperparamètres via `RandomizedSearchCV`.

## Modèle retenu : LogisticRegression

### Justification du choix

Le **recall** a été priorisé sur la précision globale (F1) : l'enjeu métier
est de **détecter un maximum de départs potentiels**, quitte à générer plus
de faux positifs (des employés signalés à risque qui, finalement, restent).
Un faux négatif (un départ non anticipé) coûte plus cher à l'entreprise qu'un
faux positif (une attention RH portée à tort).

La LogisticRegression offre en plus une **interprétabilité native** (coefficients,
analyse SHAP déjà réalisée dans le notebook source), facilitant l'explication
des prédictions aux équipes RH — un vrai avantage pour l'adoption métier d'un
outil de ce type.

### Seuil de décision

**Seuil retenu : 0.40** (probabilité de départ ≥ 0.40 ⇒ prédiction "Démission").

Un seuil abaissé par rapport au défaut classique de 0.50 : cohérent avec la
priorisation du recall — on préfère signaler plus large plutôt que de rater
des départs réels.

## Limites connues du modèle

- **Pas de ré-entraînement automatisé** : le modèle est figé au moment de son
  export (`models/model_pipeline.joblib`). Toute dérive des données RH dans le
  temps (*data drift*) ne serait pas détectée automatiquement.
- **Pas de monitoring de performance en production** : aucune mesure continue
  de la qualité des prédictions une fois déployé (pas de comparaison
  prédiction vs. réalité observée a posteriori).
- **Biais potentiels non audités formellement** : les variables comme `genre`
  ou `age` sont utilisées en entrée sans audit d'équité (fairness) dédié —
  point de vigilance si le modèle devait réellement influencer des décisions
  RH individuelles.
- **Échantillon d'entraînement figé dans le temps** : le modèle reflète les
  dynamiques RH de Futurisys au moment de la collecte des données, pas
  nécessairement les tendances actuelles.

## Protocole de mise à jour (recommandation)

En l'état, aucun ré-entraînement automatisé n'est en place (hors périmètre de
ce POC). Pour une mise en production réelle, il serait recommandé de :

1. Collecter les nouvelles données RH (avec les vrais résultats observés :
   l'employé est-il réellement parti ?) via la table `predictions` déjà en place
2. Ré-entraîner périodiquement (ex : trimestriel) sur un jeu de données étendu
3. Comparer les performances du nouveau modèle à l'ancien avant remplacement
   (non-régression)
4. Versionner chaque nouvelle version du modèle (ex : `model_pipeline_v2.joblib`)
   plutôt que d'écraser silencieusement l'existant

## Fichiers associés

- `models/model_pipeline.joblib` — pipeline complet entraîné (preprocessing + modèle)
- `models/model_metadata.json` — colonnes attendues, seuil de décision, labels
- `notebooks/Projet_4_PELLETER_Cheun.ipynb` — notebook source (exploration, comparaison, entraînement, export)