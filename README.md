
# ⭐ Fragment API — Бесплатное API для покупки звёзд и Premium / Free API for Buying Stars and Premium

## 🇷🇺 Русская версия

**Приветствую!**  
Это мини-документация по бесплатному API для покупки звёзд и Premium на [Fragment](https://fragment.com/).  
Проект был создан, чтобы вы могли напрямую взаимодействовать с API Fragment **без сторонних сервисов**.

**Разработчик:** [@vgrey46](https://t.me/vgrey46)  
Вы всегда можете написать мне и получить помощь.

---

### Обновление 2.0
Мы добавили покупку Telegram Premium [3, 6, 12] месяцев!

### ⚙️ Подготовка и настройка

#### 1. Получение `FRAGMENT_HASH`

1. Откройте [fragment.com/stars/buy](https://fragment.com/stars/buy) в браузере (например, **Microsoft Edge**).
2. Нажмите `F12` (или ПКМ → Инструменты разработчика) → вкладка **Network**.
3. Кликните на поле выбора количества звёзд (например, **50 Stars**).
4. В появившемся запросе найдите `api?hash=...` и скопируйте **значение после знака `=`**.
5. Вставьте его в переменную `FRAGMENT_HASH`.

#### 2. Получение cookie-данных

Привяжите ваш кошелёк **v4r2** к Fragment. Далее получите переменные:

- `stel_token`
- `stel_ssid`
- `stel_ton_token`

**Способы:**
- С помощью [Cookie Editor (Chrome)](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
- Через Инструменты разработчика браузера (раздел Application → Cookies)

#### 3. Получение API-ключа от [TONAPI.io](https://tonapi.io/)

1. Зарегистрируйтесь на [TONAPI.io](https://tonapi.io/)
2. Перейдите в раздел **TON API → API KEYS**
3. Скопируйте ключ и вставьте в переменную `TONAPI_KEY`

#### 4. Добавление мнемонической фразы

Укажите **24 слова** от вашего v4r2-кошелька:

```python
MNEMONIC: List[str] = [
  "", "", "", "", "", "",
  "", "", "", "", "", "",
  "", "", "", "", "", "",
  "", "", "", "", "", ""
]
```

#### 5. (Опционально) Замена User-Agent

Вы можете заменить `User-Agent`, используя значения из браузера (Инструменты разработчика → Network → Headers).

### 🚀 Запуск

```bash
sudo apt-get update -y
sudo apt-get -y install uvicorn
sudo uvicorn api:app --host 0.0.0.0 --port 80
```

Документация будет доступна по адресу:  
`http://<ваш-ip-адрес>/docs`

> Не забудьте открыть 80 порт на сервере.

### 🛰️ Пример запроса

```bash
curl -X POST http://<ВАШ_IP>/api/buyStars   -H "Content-Type: application/json"   -d '{
    "username": "string",
    "quantity": 50,
    "hide_sender": 0
}'
```

### ✅ Готово!

Поздравляю с настройкой!  
По всем вопросам, предложениям и помощи — пишите: [@vgrey46](https://t.me/vgrey46)

P.S не делал конкретные ответы сервера, но я думаю вы сможете их проинспектировать самостоятельно.

### 💎 Наш чат

Вступайте в наш чат - https://t.me/fragmentapioff

### 😄 Поддержать проект монеткой

Если проект оказался полезным и вы хотите выразить благодарность — буду рад донату в TON:

**TON-адрес:**  
`UQCSQsHC3A3yz_gHAhYmDug6JJZStmp4rhshV6C6VLf8k9Hf`

---

## 🇬🇧 English Version

**Welcome!**  
This is a mini-documentation for the free API for buying Stars and Premium on [Fragment](https://fragment.com/).  
The project was created so that you can interact directly with the Fragment API **without third-party services**.

**Developer:** [@vgrey46](https://t.me/vgrey46)  
Feel free to contact me for help.

---

### Update 2.0
We have added the purchase of Telegram Premium (3, 6, 12 months)!

### ⚙️ Preparation and Setup

#### 1. Obtaining `FRAGMENT_HASH`

1. Open [fragment.com/stars/buy](https://fragment.com/stars/buy) in your browser (e.g., **Microsoft Edge**).
2. Press `F12` (or right-click → Developer Tools) → **Network** tab.
3. Click on the star quantity selector (e.g., **50 Stars**).
4. In the request that appears, find `api?hash=...` and copy the **value after the `=` sign**.
5. Paste it into the `FRAGMENT_HASH` variable.

#### 2. Getting Cookie Data

Link your **v4r2** wallet to Fragment. Then get the following variables:

- `stel_token`
- `stel_ssid`
- `stel_ton_token`

**Methods:**
- Using [Cookie Editor (Chrome)](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
- Through Browser Developer Tools (Application → Cookies section)

#### 3. Getting an API Key from [TONAPI.io](https://tonapi.io/)

1. Sign up at [TONAPI.io](https://tonapi.io/)
2. Go to **TON API → API KEYS**
3. Copy the key and paste it into the `TONAPI_KEY` variable

#### 4. Adding the Mnemonic Phrase

Provide the **24 words** from your v4r2 wallet:

```python
MNEMONIC: List[str] = [
  "", "", "", "", "", "",
  "", "", "", "", "", "",
  "", "", "", "", "", "",
  "", "", "", "", "", ""
]
```

#### 5. (Optional) Changing the User-Agent

You can change the `User-Agent` using values from your browser (Developer Tools → Network → Headers).

### 🚀 Running

```bash
sudo apt-get update -y
sudo apt-get -y install uvicorn
sudo uvicorn api:app --host 0.0.0.0 --port 80
```

The documentation will be available at:  
`http://<your-ip-address>/docs`

> Don't forget to open port 80 on your server.

### 🛰️ Example Request

```bash
curl -X POST http://<YOUR_IP>/api/buyStars   -H "Content-Type: application/json"   -d '{
    "username": "string",
    "quantity": 50,
    "hide_sender": 0
}'
```

### ✅ Done!

Congratulations on the setup!  
For any questions, suggestions, or help — write to: [@vgrey46](https://t.me/vgrey46)

P.S I didn't implement specific server responses, but I think you can inspect them yourself.

### 💎 Our Chat

Join our chat - https://t.me/fragmentapioff

### 😄 Support the Project with a Donation

If the project was useful and you want to show your appreciation — I would be happy to receive a donation in TON:

**TON Address:**  
`UQCSQsHC3A3yz_gHAhYmDug6JJZStmp4rhshV6C6VLf8k9Hf`