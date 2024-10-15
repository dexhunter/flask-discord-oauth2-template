## Flask Discord Oauth Template

You need to setup .env
```
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=
DISCORD_REDIRECT_URI=
```

also update `DISCORD_REDIRECT_URI` for your domain and set `OAUTHLIB_INSECURE_TRANSPORT` to false in production.

and run commands to run

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
python main.py
```