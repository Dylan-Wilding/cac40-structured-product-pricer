# ReadMe file is in both English [EN], and French [FR] below. 

# 🌍 [EN] Structured Product Pricing via Monte Carlo

Academic project focused on pricing a path-dependent, capital-guaranteed structured product linked to the CAC 40 index. The model relies on Monte Carlo simulations (Geometric Brownian Motion) to estimate the product's value, decompose its exotic options, and analyze its sensitivities.

## ⚠️ Context & Authenticity Note

This script is an authentic, hand-coded academic project completed as part of my MSc FMI at SKEMA Business School. 

**It was deliberately written without the assistance of Large Language Models (LLMs).** The variables, logic flow, and embedded comments remain in their original French. This imperfection is intentional: it serves as an honest demonstration of my raw coding thought process, my practical understanding of financial mathematics, and my ability to independently translate complex derivative pricing theory into functional Python code.

## Payoff Structure

The product guarantees the initial capital at maturity, plus the maximum of the following three scenarios:

| Scenario | Condition | Payout |
|---|---|---|
| **Vanilla Participation** | Standard index performance | 50% of the CAC 40 growth |
| **Digital Step 1** | CAC 40 touches 120% of its initial value at least once | 10% minimum |
| **Digital Step 2** | CAC 40 touches 150% of its initial value at least once | 25% minimum |

*(Insert Payoff Graph Here: `![Payoff Graph](link-to-image.png)`)*

## What It Does

Given market parameters and historical data, the script executes the following:

1. **Parameter Estimation:** Fetches historical daily prices via `yfinance` to compute annualized volatility and expected returns.
2. **Monte Carlo Simulation:** Generates `M` random paths over `N` steps using a risk-neutral Geometric Brownian Motion model.
3. **Payoff Vectorization:** Calculates path-dependent maximums and final returns using optimized `numpy` arrays (`np.where`, `np.maximum`) to determine the client's yield.
4. **Leg Decomposition:** Isolates and prices the individual components of the product:
   - Zero-Coupon Bond (Capital guarantee)
   - Call Knock-Out (Strike 100%, KO 120%)
   - Call Knock-Out (Strike 120%, KO 150%)
   - Call Vanilla (50% participation, Strike 150%)
   - Call One-Touch Knock-Out (KO 120%, payout 10%)
   - Call One-Touch Knock-Out (KO 150%, payout 15%)
5. **Sensitivity Analysis (Greeks & Scenarios):** Stress-tests the structuring margin against interest rate drops, duration extensions, dividend yield spikes, and volatility shocks.
6. **Convergence Proof:** Demonstrates the numerical convergence of the Monte Carlo simulated Vanilla Call price toward the theoretical Black-Scholes analytical price as `M` approaches infinity.
7. **Secondary Market Repricing:** Adjusts parameters to simulate an early buyback, incorporating the bank's bid-ask spreads on rates (+4 bps) and implied volatility (+2%).

## Usage

The script is entirely self-contained. Running it will execute the full simulation and output the pricing margins and sensitivity impacts directly to the console.

```bash
python main.py
```

## Dependencies

```text
numpy
pandas
yfinance
matplotlib
scipy
```

## License

© 2026 Dylan WILDING.
This project is open-sourced under the MIT License.

---

# 🇫🇷 [FR] Valorisation d'un Produit Structuré par Monte-Carlo

Projet académique axé sur la valorisation d'un produit structuré garanti en capital, dépendant de la trajectoire du sous-jacent (CAC 40). Le modèle s'appuie sur des simulations de Monte-Carlo (Mouvement Brownien Géométrique) pour estimer la valeur du produit, décomposer ses options exotiques et analyser ses sensibilités de marge pour le banquier structurateur.

## ⚠️ Contexte & Authenticité

Ce script est un projet académique authentique et codé à la main, réalisé dans le cadre de mon Master of Science FMI (Financial Markets & Investments) à SKEMA Business School.

**Il a été délibérément écrit dans son intégralité sans l'assistance de Grands Modèles de Langage (LLMs).** Les variables, la logique de développement et les commentaires intégrés restent dans leur version française d'origine. Cette "imperfection" est intentionnelle : elle se veut être une démonstration honnête de mon processus brut de réflexion algorithmique, de ma compréhension pratique des mathématiques financières, et de ma capacité à traduire de manière autonome la théorie complexe du "pricing" en code Python fonctionnel.

## Structure du Produit (Payoff)

Le produit garantit l'intégralité du capital initial à maturité, auquel s'ajoute le maximum entre les trois scénarios de remboursement suivants :

| Scénario | Condition de déclenchement | Payout de Performance |
|---|---|---|
| **Participation Vanille** | Croissance classique de l'indice | 50% de la hausse du CAC 40 |
| **Digitale Palier 1** | Le CAC 40 touche 120% de sa valeur initiale au moins une fois | 10% minimum |
| **Digitale Palier 2** | Le CAC 40 touche 150% de sa valeur initiale au moins une fois | 25% minimum |

*(Insérer Graphique de Payoff Ici: `![Payoff Graph](link-to-image.png)`)*

## Fonctionnement du Code

À l'aide de données historiques et de paramètres de marché, le script exécute les opérations suivantes :

1. **Estimation des Paramètres :** Récupération des prix de clôture historiques via `yfinance` pour le calcul de la volatilité annualisée.
2. **Moteur Monte-Carlo :** Génération de `M` trajectoires aléatoires sur `N` étapes (jours) selon un modèle de Mouvement Brownien Géométrique.
3. **Vectorisation du Payoff :** Calcul des sommets locaux (`path_max`) et rendements finaux via des arrays `numpy` optimisés (`np.where`, `np.maximum`).
4. **Décomposition des Legs (Briques de Base) :** Isolation mathématique et tarification de chaque composant du produit :
   - Zéro Coupon (Garantie de Capital)
   - Call Knock-Outs
   - Calls Digitalisés "One-Touch"
   - Call Vanille Européen
5. **Analyse des Sensibilités (Grecques) :** Tests de choc sur la marge de structuration en réponse à des baisses de rentabilité, extensions de maturité, chocs de dividendes ou stress de volatilité.
6. **Preuve de Convergence :** Démonstration par incréments exponentiels de la convergence parfaite du prix Monte-Carlo du Call Vanille vers son exact prix théorique analytique via Black-Scholes ($M \to \infty$).
7. **Repricing sur Marché Secondaire :** Simulation d'un rachat potentiel par la banque à 1 an, incluant la formule du Prix Forward du CAC 40 ainsi que l'application d'un *Bid-Ask spread* défensif sur les points de la courbe (+4 bps) et sur le *Sourire de Volatilité* (+2%).

## Lancement

Le projet tourne de façon totalement autonome en important lui-même les prix du marché historique via l'API Yahoo Finance.

```bash
python main.py
```
