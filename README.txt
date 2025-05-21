# Logistics Tracking System

這是一套物流訂單提醒系統，支援每日查詢物流狀態，並顯示超過3天未取件的訂單，手動發送提醒信。

## 如何部署到 Render.com

1. 登入 GitHub 並建立新的 Repository
2. 上傳所有這些檔案（不要上傳 zip）
3. 登入 Render.com → New Web Service
4. 選擇這個 repo → 設定：
   - Build command: pip install -r requirements.txt
   - Start command: python app.py
   - Free plan

完成後 Render 會給你網址可以線上使用。
