from flask import render_template
from flask import Flask, request, send_file, render_template
import pandas as pd
from playwright.sync_api import sync_playwright
import tempfile
import os
import time

app = Flask(__name__)

# ✅ This is the code that serves the homepage
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    ...

from flask import Flask, request, send_file, render_template
import pandas as pd
from playwright.sync_api import sync_playwright
import tempfile
import os
import time

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    df = pd.read_excel(file)

    if 'IC' not in df.columns:
        return "Missing 'IC' column in Excel file", 400

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for _, row in df.iterrows():
            ic = str(row['IC'])
            try:
                page.goto("https://kelayakan.pekab40.com.my/semakan-kelayakan", timeout=30000)
                page.fill("#nokp", ic)
                page.click("#btnSemak")
                page.wait_for_timeout(3000)
                status = page.locator("#status").inner_text()
            except Exception:
                status = "Error"
            results.append(status)
            time.sleep(1.5)
        browser.close()

    df["Eligibility Status"] = results
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(tmp.name, index=False)
    return send_file(tmp.name, as_attachment=True, download_name="results.xlsx")

if __name__ == '__main__':
    app.run(debug=True)
