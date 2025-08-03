# Risk Radar 📊

**Risk Radar** is a fully automated, dynamic Streamlit web application that analyzes the performance and sector allocation of any Indian stock portfolio you upload. It provides powerful insights into portfolio performance, sector exposure, and identifies underperformers — all in real time.

---

## 🚀 Features

### 🔍 Indian Sector Analysis
- Automatically downloads historical data for Indian sector ETFs (banking, IT, pharma, etc.)
- Calculates sector-wise CAGR to identify top-performing sectors

### 📈 Portfolio Performance Analysis
- Upload your portfolio as a CSV (ticker and weight format)
- Computes CAGR, volatility, and Sharpe ratio
- Visualizes portfolio growth over time

### 🧠 Dynamic Sector Classification
- No hardcoding: sectors are fetched live from Yahoo Finance
- Supports any valid Indian stocks

### ⚖️ Sector Comparison
- Visual bar chart comparing your portfolio’s sector allocation with top-performing Indian sectors
- Identifies sector overexposure or gaps

### 📉 Underperformer Detection
- Detects stocks with CAGR < 30% of the portfolio's CAGR
- Flags them automatically

### 💡 Smart Stock Replacement Suggestions
- Suggests replacements for weak stocks using ETFs from top sectors you're underweight in
- Helps rebalance intelligently

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **yfinance**
- **pandas**, **numpy**, **matplotlib**, **seaborn**
- **Yahoo Finance web scraping** for live sector info

---

## 📂 How to Use

1. Clone the repository:
    ```bash
    git clone https://github.com/devvratpadshala/risk-radar.git
    cd risk-radar
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the app:
    ```bash
    streamlit run app.py
    ```

4. Upload your portfolio CSV file (with columns: `Ticker`, `Weight`).

---

## 📁 Portfolio File Format

Example:

| Ticker | Weight |
|--------|--------|
| TCS.NS | 0.2    |
| HDFCBANK.NS | 0.3 |
| RELIANCE.NS | 0.5 |

- Tickers should be in NSE format (e.g., `TCS.NS`, `INFY.NS`, etc.)

---

## 📊 Output Includes

- Portfolio CAGR, volatility, and Sharpe ratio
- Sector allocation vs Indian sector benchmarks
- Underperforming stocks list
- Suggested replacements (based on top sectors)

---

## 📌 Notes

- Real-time sector info scraped from Yahoo Finance
- Fully dynamic — no need to manually edit mappings
- Designed specifically for **Indian equities**

---

## 🔒 License

This project is for educational and analytical use only. Please use responsibly.

---

## 👨‍💻 Author

[Devvrat Padshala](https://github.com/devvratpadshala)
