檔案說明
===
- ### ``background.py`` : class Background
- ### ``buff.py`` : class Buff
- ### ``config.py`` : 常數、全域變數、pygame 初始化 -> <mark>變數從這裡引用</mark>
- ### ``draw.py`` : 所有有關繪製的函數 (文字、一般圖像、影子玩家) 
- ### ``main.py`` : 主程式 -> <mark>執行這裡</mark>
- ### ``network.py`` : 跟雙人模式相關的所有函式 -> <mark>IP 在這裡改</mark>
- ### ``obstacle.py`` : class Obstacle
- ### ``player.py`` : class Player
- ### ``reset.py`` : reset 函式
- ### ``server.py`` : 伺服器
環境設置
===
- ### ``python version`` : 3.13.13 [link](https://www.python.org/downloads/release/python-31313/)

> [!CAUTION]
> ### ⚠️ Windows 安裝特別注意
> 下載並執行安裝檔時，請務必勾選第一頁最下方的：
> **`[x] Add python.exe to PATH`**
> 
> *如果沒勾到，請移除後重新安裝，否則後續指令將無法執行。*

- ### 快速環境建置 (Windows)
在 VS Code 終端機 (PowerShell) 直接貼上這行指令即可：

```powershell
py -3.13 -m venv venv; .\venv\Scripts\Activate.ps1; python -m pip install --upgrade pip; pip install -r requirements.txt