# 一個可連結OpenAI API的discord機器人
## .env
DCTOKEN = (discord bot token) <br>
GPTTOKEN = (OpenAI API token) <br>
OWNERID = (機器人擁有者discord id) <br>
GPTMODEL = gpt-3.5-turbo (GPT模型) <br>
COOLDOWN = 10 (秒，GPT請求間隔) <br>
LIMIT = 20 (限制保留對話紀錄數量) <br>

* GPTMODEL為請求對話時使用的模型，若預算充足，可填gpt-4o，效果(理論上)更佳
* COOLDOWN用來防止被一堆訊息灌入，導致請求過多被限速(或者是帳單暴漲)，若預算充足、想做無隔聊天可設0
* LIMIT為限制保留用戶+GPT的對話紀錄數量，因要做到連續對話須將過去用戶與GPT的所有對話一起送出，單次對話價格會越來越高
* 記得把括號去掉

## base_prompt.txt
可給與GPT人設，"base_prompt copy.txt"為示範檔案，可自行視需求加入需要的內容 <br>
**注意**，記得把檔案名稱改為**base_prompt.txt"**

## 使用方式
此機器人有四種指令:
* /load_prompt 可重新載入base_prompt.txt，用於未關閉機器人時修改人設內容
* /history 可查看機器人儲存的對話紀錄 **注意** 因加上人設訊息字數容易超過discord上限，因此不一定能被傳出，遇此情況請直接查看程式運作的console(視窗)
* /clear_history 清除對話紀錄
* /change_prompt filename: (filename) 可更改人設檔案，通常用於測試回覆內容，並搭配/clear_history
**注意**，以上指令只有擁有者可使用，其他人嘗試使用都~~是傻逼~~會被紀錄於console
