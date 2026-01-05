from sklearn.preprocessing import MinMaxScaler
import numpy as np

scaler = MinMaxScaler()

def train(values):
    X = np.array(values)
    scaler.fit(X)

def classify(sales, profit, roe):
    X = scaler.transform([[sales, profit, roe]])[0]

    pros = []
    cons = []

    if X[0] > 0.6:
        pros.append(f"Strong sales growth of {sales}%")
    else:
        cons.append(f"Weak sales growth of {sales}%")

    if X[1] > 0.6:
        pros.append(f"Good profit growth of {profit}%")
    else:
        cons.append(f"Low profit growth of {profit}%")

    if X[2] > 0.6:
        pros.append(f"High ROE of {roe}%")
    else:
        cons.append(f"Low ROE of {roe}%")

    return pros[:3], cons[:3]
