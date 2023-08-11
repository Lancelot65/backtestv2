import ccxt, pandas as pd, matplotlib.pyplot as plt, sys, indicateur_techniques as ind, yfinance as yf
sys.path.append('../Ohlcvplus')
from ohlcv import OhlcvPlus
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

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
    
    def adapt_time(self, unit ,nametime):
        self.data[nametime] = pd.to_datetime(self.data[nametime], unit=unit).apply(mdates.date2num)
    
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

    
    def graphique(self, *args, interval=5, width_bougie=0.0002):
        df = self.data[['timestamp', 'open', 'high', 'low', 'close']]
        plt.close()
        
        def joli():
            plt.xticks(rotation=45, ha='right')
            plt.style.use('dark_background')
            plt.rcParams['font.size'] = 5
            plt.tight_layout()
            plt.subplots_adjust(wspace=0, hspace=0.5)
        
        if len(args) > 1:
            fig, axs = plt.subplots(len(args), figsize=(5, 2 * len(args)), dpi=200)

            candlestick_ohlc(axs[0], df.values, colorup='g', colordown='r', width=width_bougie, alpha=0.9)
            
            for ax in axs:
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.tick_params(axis='both', which='both', length=0)
                ax.set_axisbelow(True)
                ax.grid(axis='y', color='#073244', alpha=0.5)
                ax.grid(axis='x', color='#073244', alpha=0.2)
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %H:%M'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
            
            for i in range(len(args)):
                for ind in args[i]:
                    axs[i].plot(df['timestamp'], ind[0], color=ind[2], linewidth=ind[1], alpha=ind[3])
            
            joli()
        
        elif len(args) == 1:
            fig, ax = plt.subplots(figsize=(5, 2), dpi=200)
            
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %H:%M'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
            
            candlestick_ohlc(ax, df.values, colorup='g', colordown='r', width=width_bougie, alpha=0.9)

            joli()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.tick_params(axis='both', which='both', length=0)
            ax.set_axisbelow(True)
            ax.grid(axis='y', color='#073244', alpha=0.5)
            ax.grid(axis='x', color='#073244', alpha=0.2)
            
            for ind in args[0]:
                plt.plot(df['timestamp'], ind[0], color=ind[2], linewidth=ind[1], alpha=ind[3])
        
        else:
            fig, ax = plt.subplots(figsize=(5, 2), dpi=200)
            
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %H:%M'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
            
            candlestick_ohlc(ax, df.values, colorup='g', colordown='r', width=width_bougie, alpha=0.9)
            
            joli()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.tick_params(axis='both', which='both', length=0)
            ax.set_axisbelow(True)
            ax.grid(axis='y', color='#073244', alpha=0.5)
            ax.grid(axis='x', color='#073244', alpha=0.2)

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
    
    def backtest(self, signal_achat, signal_vente, stop_loss=None, take_profit=None):
        for i in range(len(self.close)):
            if signal_achat[i] == True:
                self.open_pos(i, take_profit, stop_loss)
            elif signal_vente[i] == True:
                self.close_pos(i)
            
            self.updates(i)
        print(self.all_position)