from flask import Flask
from flask import render_template,request

#import textblob
import transformers
from transformers import pipeline
classifier = pipeline("sentiment-analysis")

import os
import google.generativeai as genai

api = os.getenv('makersuite')
genai.configure(api_key=api)
model = genai.GenerativeModel('gemini-1.5-flash')

import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
def get_basic_company_info(stock_code):
    """
    获取单个公司的基本信息，并以字典格式返回。
    """
    ticker = yf.Ticker(stock_code)
    info = ticker.info

    company_data = {
        "Stock Code": stock_code,
        "Company Name": info.get('longName', 'N/A'),
        "Location": f"{info.get('country', 'N/A')}, {info.get('city', 'N/A')}",
        "Sector": info.get('sector', 'N/A'),
        "Industry": info.get('industry', 'N/A'),
        "Employees": info.get('fullTimeEmployees', 'N/A'),
        "Company Summary": info.get('longBusinessSummary', 'N/A'),
        "Website": info.get('website', 'N/A')
    }
    
    return company_data

def plot_stock_price(stock_code):
    """
    绘制公司股价走势图（最近 1 年），并保存为静态文件。
    """
    ticker = yf.Ticker(stock_code)
    hist = ticker.history(period="1y")  # 过去 1 年的股价数据

    if hist.empty:
        return None  # 如果没有数据，返回 None
    
    plt.figure(figsize=(10, 5))
    plt.plot(hist.index, hist['Close'], label=f"{stock_code} Closing Price", color='blue')

    plt.title(f"{stock_code} Stock Price (Last 1 Year)")
    plt.xlabel("Date")
    plt.ylabel("Closing Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    img_path = f"static/{stock_code}_stock.png"
    plt.savefig(img_path)
    plt.close()

    return img_path  # 返回图片路径


app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/main",methods=["GET","POST"])
def main():
    name = request.form.get("q")
    return(render_template("main.html"))

@app.route("/SA",methods=["GET","POST"])
def SA():
    return(render_template("SA.html"))

@app.route("/SA_result",methods=["GET","POST"])
def SA_result():
    q = request.form.get("q")
    r = classifier(q)
    return(render_template("SA_result.html", r=r))

@app.route("/genAI",methods=["GET","POST"])
def genAI():
    return(render_template("genAI.html"))

@app.route("/genAI_result",methods=["GET","POST"])
def genAI_result():
    q = request.form.get("q")
    r = model.generate_content(q)
    return(render_template("genAI_result.html", r=r.candidates[0].content.parts[0].text))

@app.route("/paynow",methods=["GET","POST"])
def paynow():
    return(render_template("paynow.html"))


@app.route("/stock", methods=["GET", "POST"])
def stock():
    return render_template("stock.html")

@app.route("/stock_result", methods=["GET", "POST"])
def stock_result():
    stock_codes = request.form.get("q").strip().upper()

    if not stock_codes:
        return render_template("stock.html", error="❌ 请输入有效的股票代码！")
    
    stock_list = [code.strip() for code in stock_codes.split(",")]

    results = []
    images = []

    for stock_code in stock_list:
        try:
            company_info = get_basic_company_info(stock_code)
            results.append(company_info)

            img_path = plot_stock_price(stock_code)
            if img_path:
                images.append({"stock_code": stock_code, "image_path": img_path})
        except Exception as e:
            results.append({"Stock Code": stock_code, "Error": f"⚠️ 无法获取数据: {e}"})

    return render_template("stock_result.html", results=results, images=images)






























if __name__ == "__main__":
    app.run()
