"""

L'instrument qu'on essaie de pricer est un produit structuré, dont le rendement est déterminé comme suit :

"A maturité le client est remboursé de son capital initial plus le maximum entre :
- 50% de la hausse du CAC 40 sur la période, 
- 10%, si le CAC 40 a touché au moins une fois durant la vie du produit 120% du 
CAC 40 initial,  
- 25%, si le CAC 40 a touché au moins une fois durant la vie du produit 150% du 
CAC 40 initial." 

Ainsi, puisqu'il n'existe pas de "closed-form" solution à ce produit, et que par ailleurs,
le rendement dépend du chemin suivi par le CAC40 (et non simplement de la valeur finale de ce dernier),
nous allons utiliser la méthode de Monte-Carlo pour estimer la valeur de ce produit. 


"""

import numpy as np
import pandas as pd 
import yfinance as yf
import matplotlib.pyplot as plt
import scipy.stats as stats

# ETAPE 1 : Récupération des prix quotidiens du CAC40 via yfinance pour estimation des paramètres (volatilité)
# Pour le taux de dividendes et le rf rate ce n'est pas pertinent de le faire de cette manière, je l'ai donc hard codé. 

tickers = ["^FCHI"]
start = "2021-01-01"
end = "2026-03-20"

rf = 0.0455 # Issu de l'onglet "Courbe des Taux" de l'excel de l'assignment. 
q = 0.03 # Taux de dividendes approximatif du CAC40. 
trading_days = 256
dt = 1/trading_days
t = 3
N = t * trading_days
M = 100000

prices_CAC = yf.download(tickers, start=start, end=end)['Close']
s0 = prices_CAC.iloc[-1, 0]
returns = np.array(prices_CAC.pct_change().dropna())
mu = np.mean(returns)*trading_days
vol = np.std(returns, axis=0)*np.sqrt(trading_days)

# ETAPE 2 : Simulation du CAC40 via MC. Les paramètres utilisés sont déduits de 5 ans de données historiques. 
def run_pricer_MC(s0, rf, q, vol, t, M, N, InclureIntervaleConf=False):
    
    Z = np.random.standard_normal((N, M))

    daily_log_returns = (rf - q - 0.5 * vol**2)*dt + vol*np.sqrt(dt)*Z
    cum_log_returns = np.cumsum(daily_log_returns, axis=0)

    prices_matrix = np.zeros((N+1, M))
    prices_matrix[0,:] = s0
    prices_matrix[1:,:] = s0 * np.exp(cum_log_returns)
    prices = pd.DataFrame(prices_matrix)

    # plt.plot(prices)
    # plt.title("Simulated CAC40 Prices")
    # plt.xlabel("Time")
    # plt.ylabel("Price")
    # plt.show()

    # Il faut désormais tester si le CAC40 touche le seuil de 120, 150. 
    path_max = np.max(prices_matrix, axis = 0)
    path_min = np.min(prices_matrix, axis = 0)
    lock = np.where(path_max >= (prices_CAC.iloc[-1, 0]) * 1.5, 0.25, np.where(path_max >= (prices_CAC.iloc[-1, 0])* 1.2, 0.1, 0))

    # Calcul de la croissance du CAC40 sur la période pour chaque simulation
    perf = prices.iloc[-1] / (prices_CAC.iloc[-1, 0]) -1 

    # Vérification de la cohérence du modèle. La moyenne des rendements simulés devrait être proche de l'espérance du CAC40.
    moyenne_perf = np.mean((1 + perf) * s0)
    esperance_CAC = np.exp((rf-q)*t) * s0

    # Calcul du rendement du client sur la période pour chaque simulation. 
    payoff = 1 + np.maximum(np.maximum(0.5*perf, lock), 0.0)

    # Calcul de la valeur actuelle du produit, basé sur la moyenne des simulations, et déduction de la marge
    pv_payoff = np.exp(-rf*t) * np.mean(payoff)
    marge = 1 - pv_payoff

    # Calcul de l'intervale de confiance du payoff 
    intervale_conf = np.std(payoff)/np.sqrt(M)
    if InclureIntervaleConf:
        demi_largeur = 1.96 * intervale_conf
        print(f"Intervale de confiance (95%): [{(1 -(pv_payoff - demi_largeur))*100:.2f}% :{(1 - (pv_payoff + demi_largeur))*100:.2f}%]")
    # print("Intervale conf = ", (intervale_conf*100), "%")

    # Nous avons la valeur actualisée du produit dans son ensemble (env. 0.98). 
    # Maintenant il faut calculer la valeur de chaque leg de ce produit (toutes les options individuellement). 

    # Instrument 1 : Le ZCB (pour garantir le capital). 
    zcb_price = 1 * np.exp(-rf*t)

    # Intrument 2 : Call Knock-Out (Strike 100, KO 120)
    KO1_payoff = np.where(path_max >= 1.2*s0, 0, np.maximum(0.5*perf,0))
    KO1_price = np.exp(-rf*t) * np.mean(KO1_payoff)

    # Intrument 3 : Call Knock-Out (Strike 120, KO 150)
    KO2_payoff = np.where(path_max >= 1.5*s0, 0, np.maximum(0.5*(perf - 0.2),0))
    KO2_price = np.exp(-rf*t) * np.mean(KO2_payoff)

    # Instrument 4 : Call Vanilla, 50%, strike 150
    vanilla_payoff = 0.5 * np.maximum(perf - 0.5, 0) 
    vanilla_price = np.exp(-rf*t) * np.mean(vanilla_payoff)

    # Intrument 5 : Call One-Touch Knock Out (KO 120, payout 10%)
    OT1_payoff = np.where(path_max >= 1.2*s0, 0.1, 0)
    OT1_price = np.exp(-rf*t) * np.mean(OT1_payoff)

    # Intrument 6 : Call One-Touch Knock Out (KO 150, payout 15%)
    OT2_payoff = np.where(path_max >= 1.5*s0, 0.15, 0)
    OT2_price = np.exp(-rf*t) * np.mean(OT2_payoff)

    product_components = [zcb_price, KO1_price, KO2_price, vanilla_price, OT1_price, OT2_price]
    # print(f"PV of product = {pv_payoff:.4f}")
    # print("PV of the components =", sum(product_components))
    # print("PV of product rougly equal to PV of the individual components :", np.isclose(round(sum(product_components),6),round(pv_payoff, 6)))

    return marge

"""
Nous avons donc la fonction qui nous permet de calculer la valeur du produit en fonction des inputs : 
- Prix de base du CAC40 (s0)
- Taux sans risque (rf)
- Taux de dividende (q)
- Volatilité (vol)
- Maturité (t)
- Nombre de simulations (M)
- Nombre de "steps" (N)
Nous pouvons ainsi passer à l'ETAPE 3 : Regarder les sensibilités pour répondre à la partie 5 de l'assignment. 
"""

# Scénario de base 
marge_base = run_pricer_MC(s0, rf, q, vol, t, M, N, InclureIntervaleConf=True)
print(f"4.d : Marge dans scénario de base : {marge_base*100:.2f} %")

# 5.a Baisse courbe des taux de 50 bp
marge_5a = run_pricer_MC(s0, rf - 0.005, q, vol, t, M, N)
print(f"5.a : Marge si baisse des taux de 50 bps : {marge_5a*100:.2f} %, soit un impact de {(marge_5a - marge_base)*100:.2f} %")

# 5.b Solutions potentielles ? 
# Baisser la participation (ex : on a que 40% de la performance du CAC40), baisser les paiements digitaux (ex : on obtient 10% de performance que si le CAC40 touche les 30%, et non pas 20%).

# 5.c Alongement de la durée de placement de 1 an 
taux_zcb_4ans = 0.047
marge_5c = run_pricer_MC(s0, taux_zcb_4ans, q, vol, 4, M, trading_days*4)
print(f"5.c : Marge si durée allongée de 1 an : {marge_5c*100:.2f} %, soit un impact de {(marge_5c - marge_base)*100:.2f} %")

# 5.d Hausse du (coupon?) yield en dividendes de 1%
marge_5d = run_pricer_MC(s0, rf, q+0.01, vol, t, M, N)
print(f"5.d : Marge si dividende yield augmenté de 1% : {marge_5d*100:.2f} %, soit un impact de {(marge_5d - marge_base)*100:.2f} %")

# 5.e Hausse de la volatilité de 1%
marge_5e = run_pricer_MC(s0, rf, q, vol+0.01, t, M, N)
print(f"5.e : Marge si volatilité augmentée de 1% : {marge_5e*100:.2f} %, soit un impact de {(marge_5e - marge_base)*100:.2f} %")

# 5.f Observation de la convergence entre la valo du Call Vanille par B&S et par MC en fonction du nombre de simulations : 
def bs_call(S, K, T, r, q, vol): 
    d1 = (np.log(S / K) + (r - q + 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    d2 = (np.log(S / K) + (r - q - 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    prix_call_BS = (S * np.exp(-q * T) * stats.norm.cdf(d1)) - (K * np.exp(-r * T) * stats.norm.cdf(d2))
    prix_call_BS = (prix_call_BS/2)/S # Car c'est pour 50% du nominal, et on le veux en % du spot pour pouvoir le comparer au MC.
    print("5.f : Prix du Call via B&S :", prix_call_BS) 
    return prix_call_BS
bs_call(s0, 1.5*s0, t, rf, q, vol)

# On a donc la valeur du Call via B&S. On va maintenant le valoriser via MC. 

def run_vanilla_MC(s0, rf, q, vol, t, M, N):
    Z = np.random.standard_normal((N, M))
    daily_log_returns = (rf - q - 0.5 * vol**2)*dt + vol*np.sqrt(dt)*Z
    cum_log_returns = np.cumsum(daily_log_returns, axis=0)

    prices_matrix = np.zeros((N+1, M))
    prices_matrix[0,:] = s0
    prices_matrix[1:,:] = s0 * np.exp(cum_log_returns)
    prices = pd.DataFrame(prices_matrix)
    perf = prices.iloc[-1] / s0 -1

    vanilla_payoff = 0.5 * np.maximum(perf - 0.5, 0) 
    vanilla_price = np.exp(-rf*t) * np.mean(vanilla_payoff)
    
    return vanilla_price

# Pour observer la "convergence" de cette valo avec le MC, il faut varier le nombre de simulations. 
# Il faut donc utiliser cette boucle qui va faire tourner la simulation en entier pour M = 10, 100, 1000, 10000, 100000. 

for M in [1000, 10000, 200000]:
    vanilla_price = run_vanilla_MC(s0, rf, q, vol, t, M, N)
    print(f"5.f : Prix du Call via MC avec {M} simulations : {vanilla_price:.4f}")
print("Nous observons que lorsque le nombre de simulations augmente, la valeur du call via MC se rapproche du prix du call via B&S.")

"""
Nous avons donc répondu à toutes les questions de sensibilités de la partie 5 : 
Nous pouvons ainsi passer à l'ETAPE 4 : Modélisation le marché secondaire pour répondre à la partie 6 de l'assignment. 
"""

t_restant = t - 1 # On retire 1 an à la maturité
N_restant = t_restant * trading_days
s_forward = s0 * np.exp((rf-q)*1)

bid_spread_banque = 0.0004 #4bps 
spread_vol_banque = 0.02

# On fait tourner notre MC en considération des spreads de la banque sur le taux et sur la vol. 
marge_secondaire = run_pricer_MC(s_forward, (rf + bid_spread_banque), q, (vol + spread_vol_banque), t_restant, M, N_restant)
print(f"6.a : Marge dans le marché secondaire : {marge_secondaire*100:.2f} %")

# Maintenant on connait notre marge, donc on est prêt à 'racheter' le produit pour au plus : 
prix_rachat = 1 - marge_secondaire; print(f"6.b : Prix le plus élevé auquel on accepterait de racheter le produit : {prix_rachat*100:.2f} %")