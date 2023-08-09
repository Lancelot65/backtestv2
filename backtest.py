import ccxt, pandas as pd, matplotlib.pyplot as plt, sys, indicateur_techniques as ind
sys.path.append('../Ohlcvplus')
from ohlcv import OhlcvPlus

class Backtest:
    def __init__(self):
        self.evolution = 0
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

    def load_crypto(self, symbol='BTC/USDT', time='30m', length=-1, sinces='2023-01-01 00:00:00'):
		
        ohlcvp = OhlcvPlus(ccxt.binance())
        self.data = ohlcvp.load(market=symbol, timeframe=time, since=sinces, limit=length, update=True, verbose=True, workers=100)
        self.close = self.data.close
    
    def load_eur_usd(self, symbol='EUR/USD', time='30m', length=-1, sinces='2023-01-01 00:00:00'):
		
        ohlcvp = OhlcvPlus(ccxt.bybit())
        self.data = ohlcvp.load(market=symbol, timeframe=time, since=sinces, limit=length, update=True, verbose=True, workers=100)
        self.close = self.data.close
        
    def export_csv(self, name):
        self.data.to_csv(name)
    
    def import_csv(self, name, longeur):
        self.data = pd.read_csv(name).head(longeur)
        self.close = self.data.close
    
    def open_pos(self, pos:int, take_profit=None, stop_loss=None):
        if self.position is None:
            self.position = [self.close[pos], pos]

            if take_profit:
                self.take_profit = take_profit
            
            if stop_loss:
                self.stop_loss = stop_loss
    
    def close_pos(self, pos:int):
        if self.position is not None:
            self.evolution += (self.close[pos] - self.position[0]) / self.position[0]
            
            add_ligne = pd.DataFrame({
                    "open_pos" : [self.position[1]],
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
            axs[0].plot(self.data.timestamp, self.close)
            for i in range(len(args)):
                for ind in args[i]:
                    axs[i].plot(self.data.timestamp, ind)
            
            for row in range(len(self.all_position)):
                ou = self.all_position['open_pos'].iloc[row]
                x = self.data.timestamp[ou]
                y = self.close[ou]
                axs[0].plot(x, y, marker='^', markersize=10, color='g', label='Triangles')
                
                ou = self.all_position['close_pos'].iloc[row]
                x = self.data.timestamp[ou]
                y = self.close[ou]
                axs[0].plot(x, y, marker='v', markersize=10, color='r', label='Triangles')
            plt.subplots_adjust(wspace=0)
            plt.show()

        elif len(args) != 0:
            fig, axs = plt.subplots()
            axs.plot(self.data.timestamp, self.close)
            for ind in args[0]:
                axs.plot(self.data.timestamp, ind)
            for row in range(len(self.all_position)):
                ou = self.all_position['open_pos'].iloc[row]
                x = self.data.timestamp[ou]
                y = self.close[ou]
                axs.plot(x, y, marker='^', markersize=10, color='g', label='Triangles')
                
                ou = self.all_position['close_pos'].iloc[row]
                x = self.data.timestamp[ou]
                y = self.close[ou]
                axs.plot(x, y, marker='v', markersize=10, color='r', label='Triangles')
            plt.subplots_adjust(wspace=0)
            plt.show()
        else:
            fig, ax = plt.subplots()
            ax.plot(self.data.timestamp, self.close)
            for row in range(len(self.all_position)):
                ou = self.all_position['open_pos'].iloc[row]
                x = self.data.timestamp[ou]
                y = self.close[ou]
                ax.plot(x, y, marker='^', markersize=10, color='g', label='Triangles')
                
                ou = self.all_position['close_pos'].iloc[row]
                x = self.data.timestamp[ou]
                y = self.close[ou]
                ax.plot(x, y, marker='v', markersize=10, color='r', label='Triangles')
            plt.subplots_adjust(wspace=0)
            plt.show()

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
    
    def edge(self):
        evolution = ((self.close.iloc[-1] - self.close.iloc[0]) / self.close.iloc[0])
        longueur = 0
        for row in range(len(self.all_position)):
            longueur += self.all_position['close_pos'].iloc[row] - self.all_position['open_pos'].iloc[row]
        evolution_longueur = (evolution * longueur) / len(self.close)
        self.alpha = self.evolution - evolution_longueur
        print(self.alpha)

    def reset(self):
        data, close = self.data, self.close
        self.__init__()
        self.data, self.close = data, close