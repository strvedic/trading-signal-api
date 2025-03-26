import yfinance as yf
import pandas as pd
import numpy as np
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Trading Signal API is running. Use /get_signal/<stock_symbol> to fetch data."})

def get_trading_signal(stock_symbol):
    try:
        # Fetch stock data with a timeout (prevents infinite loading)
        data = yf.download(stock_symbol, period="15d", interval="1h", progress=False, timeout=10)

        # Check if data is empty (invalid stock symbol)
        if data.empty:
            return {"error": f"Invalid stock symbol: {stock_symbol}"}

        # Calculate Simple Moving Averages (SMA)
        data["SMA_20"] = data["Close"].rolling(window=20).mean()
        data["SMA_50"] = data["Close"].rolling(window=50).mean()

        # Generate Buy/Sell/Hold signal based on SMA crossover
        if data["SMA_20"].iloc[-1] > data["SMA_50"].iloc[-1]:
            signal = "BUY"
        elif data["SMA_20"].iloc[-1] < data["SMA_50"].iloc[-1]:
            signal = "SELL"
        else:
            signal = "HOLD"

        return {"stock": stock_symbol, "signal": signal}

    except Exception as e:
        return {"error": str(e)}

@app.route('/get_signal/<stock_symbol>', methods=['GET'])
def fetch_signal(stock_symbol):
    signal_data = get_trading_signal(stock_symbol)
    return jsonify(signal_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
