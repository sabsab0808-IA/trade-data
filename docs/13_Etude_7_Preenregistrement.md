---
title: Étude n°7 — Pré-enregistrement
subtitle: Swing multi-jours, dérive overnight, suivi de tendance — écrit AVANT tout calcul
num: 13
date: 2026-11-02
---

## Pourquoi cette étude

Les études 1 à 6 ont montré qu'en intraday, l'edge brut (~+0,10 R au mieux) est mangé par le coût d'un aller-retour (~0,09 R). En tenant les positions **plusieurs jours**, le mouvement visé est 10 à 50 fois plus grand, donc les coûts deviennent quasi nuls en R. On teste 3 familles connues de la littérature.

**Attention : aucune de ces stratégies n'est compatible avec Topstep** (positions fermées chaque soir). Si l'une passe, il faudra chercher un autre support (compte perso, prop firm qui autorise l'overnight) — à vérifier à ce moment-là.

Ce document est publié dans le projet avant de lancer le code. Il n'est plus modifié ensuite.

## Données

- NQ, ES, CL, GC — 1 minute, 06/2010 → 10/2026 (Databento, dépôt `trade-data`), agrégées en barres journalières.
- **IS : 2010–2020. OOS : 2021–2026** (même découpage que les études 4 à 6).
- Barre journalière = séance régulière des études 4 à 6 (NQ/ES 09:30–16:00, CL 09:00–14:30, GC 08:45–13:30, heure de New York). Séance incomplète (< 80 % des minutes) → ignorée.
- **Série continue ajustée** (méthode « Panama ») : à chaque changement de contrat (à minuit UTC, en pleine séance de nuit), on décale tout l'historique de l'écart entre le 1er prix du nouveau contrat et le dernier prix de l'ancien. Les variations en points restent exactes ; une position tenue à travers un roll paie un coût de roll.
- Honnêteté : ces 3 stratégies n'ont jamais été testées dans le projet, mais elles sont publiées depuis longtemps (le hasard du « IS » est donc déjà en partie entamé par les auteurs).

## Unité : le R

- **1 R = ATR20 journalier** (moyenne des 20 derniers true ranges, sans le jour du signal), fixé à l'entrée.
- Exemple d'ordre de grandeur : MNQ en 2026, ATR20 ≈ 300–400 points ≈ 600–800 $ par micro.
- Le P&L est **réévalué chaque jour** à la clôture (pour le Sharpe et le drawdown). Les 4 marchés pèsent le même risque (1 R chacun).

## Coûts

- 1 $ aller-retour par micro + **1 tick de glissement** sur chaque ordre au marché (entrée et sortie).
- Position tenue à travers un roll : **+1 $ et +2 ticks** (fermer l'ancien contrat, ouvrir le nouveau).
- Convertis en R avec l'ATR20 d'entrée.

## Les 3 hypothèses (paramètres figés, aucune optimisation)

**H1 · Swing de retour à la moyenne « RSI 2 »** — Connors & Alvarez (2008).
- Signal à la clôture du jour J : achat si clôture > moyenne 200 jours **et** RSI(2) < 10 ; vente si clôture < moyenne 200 jours **et** RSI(2) > 90.
- Entrée à l'ouverture de J+1 (± 1 tick).
- Sortie à l'ouverture suivante dès qu'une clôture repasse au-dessus de la moyenne 5 jours (achat) / en dessous (vente), ou au plus tard après 10 séances.
- Une position à la fois par marché. Pas de stop (comme l'original). Les côtés achat et vente sont aussi publiés séparément, à titre descriptif.

**H2 · Dérive overnight** — Kelly & Clark (2011) ; Boyarchenko, Larsen & Whelan (2023).
- Achat chaque soir à la **dernière minute de la séance** (+1 tick), revente à la **première minute de la séance suivante** (−1 tick). Week-ends inclus.
- Achat uniquement (l'hypothèse est une dérive haussière la nuit). 1 R = ATR20.

**H3 · Momentum de série temporelle 12 mois** — Moskowitz, Ooi & Pedersen (2012).
- Dernier jour de chaque mois, à la clôture : sens = signe de (clôture − clôture 252 séances avant).
- Position prise ou retournée à l'ouverture du 1er jour du mois suivant, tenue un mois. Si le sens ne change pas, pas de coût (le recalibrage de la taille est ignoré). 1 R = ATR20 recalculé chaque mois.

## Référence : buy & hold

Achat permanent des 4 marchés, même pondération (1 R = ATR20 recalculé chaque mois), coûts de roll inclus. Une stratégie qui ne fait pas mieux que ça n'a pas d'intérêt : il suffirait d'acheter et d'attendre.

## Critère de succès (par stratégie, 4 marchés combinés)

Une stratégie est retenue seulement si **les 5 conditions** sont remplies :

1. **IS 2010–2020** : Sharpe annualisé net ≥ **0,5**.
2. **IS** : borne basse de l'IC 95 % du P&L mensuel moyen > 0.
3. **OOS 2021–2026** : Sharpe net ≥ **0,3**.
4. **Cohérence** : P&L net positif sur au moins **3 des 4 marchés** en IS.
5. **Mieux que le buy & hold** : Sharpe supérieur à celui du buy & hold, **en IS et en OOS**.

3 stratégies testées : le risque de faux positif est faible, mais l'OOS et la comparaison au buy & hold restent obligatoires.

## Ce qui se passe ensuite

- Une stratégie passe → on cherche où elle est tradable (compte perso en micros, ou prop firm qui autorise l'overnight), puis forward test.
- Rien ne passe → on le dit, et la piste « swing » est fermée au même titre que l'intraday.
- Tout est publié : résultats par marché, par période, par année, gagnants ou non.
