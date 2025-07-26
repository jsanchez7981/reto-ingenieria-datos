import pandas as pd

# Clase para trabajar con las estadísticas
class StatsTracker:
    def __init__(self):
        self.count = 0
        self.sum_price = 0.0
        self.min_price = float('inf')
        self.max_price = float('-inf')
    
    def update(self, price):
        if pd.isna(price):
            return # si el campo no es numerico o esta vacio lo ignoramos
        self.count += 1
        self.sum_price += price
        self.min_price = min(self.min_price,price)
        self.max_price = max(self.max_price,price)
    
    def mean(self):
        return self.sum_price / self.count if self.count > 0 else 0
    
    def snapshot(self):
        return{
            'count': self.count,
            'mean': round(self.mean(),2),
            'min': self.min_price,
            'max': self.max_price
        }