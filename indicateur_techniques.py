import pandas as pd, matplotlib.pyplot as plt

def mm(close, length):
    return close.rolling(length).mean()


def max_period(close, length):
    return close.rolling(length).max()
def min_period(close, length):
    return close.rolling(length).min()

def ema(close, periode):
    return close.ewm(span=periode, adjust=False).mean() 
def Bande_bollinger(close, longueur=14, std_dev = 2, print_plot = False):
    sma = close.rolling(longueur).mean()
    upper_band = sma + std_dev * close.rolling(longueur).std()
    lower_band = sma - std_dev * close.rolling(longueur).std()

    df_bd = pd.DataFrame({"upper_band" : upper_band, "lower_band" : lower_band, "mm_band" : sma})
    if print_plot:
        df_bd.upper_band.plot()
        df_bd.lower_band.plot()

        x = df_bd.index
        y2 = df_bd.lower_band.values
        y1 = df_bd.upper_band.values

        plt.fill_between(x, y1, y2, where=(y1 >= y2), color='blue', alpha=0.05)

        sma.plot()
        close.plot()

    return df_bd

def MACD(close, x = 12, y = 26, z = 9):
    df_macd = pd.DataFrame()
    df_macd["MACD"] = ema(close, x) - ema(close, y)
    df_macd["emaz"] = ema(df_macd.MACD, z)

    return df_macd.MACD, df_macd.emaz

def calc_rsi(close, longueur=14):
    price_diff = close.diff().dropna()
    
    gains = price_diff.mask(price_diff <= 0, 0)
    losses = -price_diff.mask(price_diff >= 0, 0)
    
    avg_gain = gains.rolling(longueur).mean()
    avg_loss = losses.rolling(longueur).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def oscillateur_stochastique(close, longeur = 14):
    low = close.rolling(longeur).min()
    high = close.rolling(longeur).max()
    K = mm(((close - low) / (high - low)) * 100, 14)
    D = mm(K, 3)
    return K, D


def momentum(close, longueur=12):
    return close - close.shift(longueur)

def CMF(close, bas, haut, volume, longueur=21):
    multiplicateur = ((close - bas) - (haut - close)) /(haut - bas)
    volume_flux = volume * multiplicateur
    cmf = volume_flux.rolling(longueur).mean() / volume.rolling(longueur).mean()
    return cmf

def CCI(close, haut, bas):
    TP = (haut + bas + close) / 3
    ecart_type = 2
    cci = (TP - mm(TP, 20)) / (.015 * ecart_type)
    return cci

def OBV(close, volume):
    obv = [0]
    for i in range(1, len(close)):
        if close[i] > close[i-1]:
            obv.append(obv[i-1] + volume[i])
        elif close[i] < close[i-1]:
            obv.append(obv[i-1] - volume[i])
        else:
            obv.append(obv[i-1])

    return obv


def nuage_ichimoku(close, plot_nuage=False):
    tenkan_sen = (close.rolling(9).max() + close.rolling(9).min()) / 2
    kijun_sen = (close.rolling(26).max() + close.rolling(26).min()) / 2
    lagging_span = close.shift(26)
    SSA = ((tenkan_sen + kijun_sen) / 2).shift(26)
    SSB = ((close.rolling(52).max() + close.rolling(52).min()) / 2).shift(26)

    df_ichimoku = pd.DataFrame({
        'Tenkan_sen': tenkan_sen,
        'Kijun_sen': kijun_sen,
        'SSA': SSA,
        'SSB': SSB,
        'Lagging_Span': lagging_span
    })
    if plot_nuage:
        df_ichimoku.Tenkan_sen.plot(alpha=0.5, legend='Tenka', linewidth=0.6)
        df_ichimoku.Kijun_sen.plot(alpha=0.5, legend='Kijun', linewidth=0.6)
        df_ichimoku.Lagging_Span.plot(alpha=0.5, legend='lagging', linewidth=0.6)
        df_ichimoku.SSA.plot(alpha=0.5, legend='SSA', linewidth=0.6)
        df_ichimoku.SSB.plot(alpha=0.5, legend='SSB', linewidth=0.6)

        x = df_ichimoku.index
        y2 = df_ichimoku.SSA
        y1 = df_ichimoku.SSB

        plt.fill_between(x, y1, y2, where=(y1 > y2), color='red', alpha=0.05)
        plt.fill_between(x, y1, y2, where=(y1 < y2), color='green', alpha=0.05)

        close.plot(legend="close", linewidth=1, color='red')

    return df_ichimoku

def retracement_fimona(close, long=50):
    cent = close.rolling(long).max()
    zero = close.rolling(long).min()
    middle = (cent + zero) / 2
    #continuer


def ROC(close, long=12):
    return close / close.shift(long)