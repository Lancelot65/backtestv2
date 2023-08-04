import ccxt, pandas as pd, matplotlib.pyplot as plt, sys, indicateur_techniques as ind
sys.path.append('../Ohlcvplus')
from ohlcv import OhlcvPlus

class Backtest:
    def __init__(self, capital):
        self.capital = capital
        self.position = None

        self.all_position = pd.DataFrame({
			"open_pos" : [],
            "close_pos" : [],
			"mode" : [],
			"open" : [],
			"close" : []
		})

        self.stop_loss = None
        self.take_profit = None

    def load_data(self, symbol='BTC/USDT', time='30m', length=500, sinces='2023-01-01 00:00:00'):
		#telecharcgement des donnée ohlcv
        ohlcvp = OhlcvPlus(ccxt.binance(), database_path='data.db')
        self.data = ohlcvp.load(market=symbol, timeframe=time, since=sinces, limit=length, update=True, verbose=True, workers=100)
        self.close = self.data.close
    
    def copie_data(self, df):
        self.data = df
        self.close = self.data.close
    
    def open_pos(self, taille:int, pos:int, take_profit=None, stop_loss=None):
        if self.position is None:
            self.position = [self.close[pos], taille / self.close[pos], pos]
            print("open", pos)

            if take_profit:
                self.take_profit = self.close[pos] * (1 + (take_profit / 100))
            
            if stop_loss:
                self.stop_loss = self.close[pos] * (1 - (stop_loss / 100))
    
    def close_pos(self, pos:int):
        if self.position is not None:
            self.capital += (self.close[pos] - self.position[0]) * self.position[1]
            print('close', pos)
            print(self.capital)

            add_ligne = pd.DataFrame({
                    "open_pos" : [self.position[2]],
                    "close_pos" : [pos],
					"mode" : ["long"],
					"open" : [self.position[0]],
					"close" : [self.close[pos]]
				})
            self.all_position = pd.concat([self.all_position, add_ligne])
            self.position = None
    
    def graphique(self, *args:list):
        plt.close()
        if len(args) > 1:
            fig, axs = plt.subplots(len(args))
            axs[0].plot(self.close)
            for i in range(len(args)):
                for ind in args[i]:
                    axs[i].plot(ind)
            
            for row in range(len(self.all_position)):
                x = self.all_position['open_pos'].iloc[row]
                y = self.close[x]
                axs[0].plot(x, y, marker='^', markersize=10, color='g', label='Triangles')
                
                x = self.all_position['close_pos'].iloc[row]
                y = self.close[x]
                axs[0].plot(x, y, marker='v', markersize=10, color='r', label='Triangles')

        else: 
            fig, axs = plt.subplots()
            axs.plot(self.close)
            for ind in args[0]:
                axs.plot(ind)
            for row in range(len(self.all_position)):
                x = self.all_position['open_pos'].iloc[row]
                y = self.close[x]
                axs.plot(x, y, marker='^', markersize=10, color='g', label='Triangles')
                
                x = self.all_position['close_pos'].iloc[row]
                y = self.close[x]
                axs.plot(x, y, marker='v', markersize=10, color='r', label='Triangles')


    def trier_signal(self, series):
        result = []
        current_value = False
        for value in series:
            if value == current_value:
                result.append(False)
            else:
                current_value = value
                result.append(value)
        result[0] = False
        return result
    
    def updates(self, pos):
        if self.position is not None:
            self.stop_loss_take_profit(pos)
    
    def stop_loss_take_profit(self, pos):
        if self.take_profit:
            if self.take_profit < self.close[pos]:
                self.close_pos(pos)
                self.take_profit = None
        if self.stop_loss:
            if self.stop_loss > self.close[pos]:
                self.close_pos(pos)
                self.stop_loss = None