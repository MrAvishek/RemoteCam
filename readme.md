## Quick Start

Clone repository:

```bash
git clone https://github.com/MrAvishek/RemoteCam.git
cd RemoteCam
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install Cloudflare Tunnel:

```bash
winget install Cloudflare.cloudflared
```

Create `.env` file:

```env
BOT_TOKEN=YOUR_BOT_TOKEN
CHAT_ID=YOUR_CHAT_ID

USERNAME=admin
PASSWORD=1234
```

Run server:

```bash
python server.py
```

RemoteCam will:

- Start Flask camera server
- Create Cloudflare public tunnel
- Generate remote access URL
- Send live link to Telegram automatically