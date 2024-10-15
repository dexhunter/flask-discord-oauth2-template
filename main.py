import os

from flask import Flask, redirect, url_for, jsonify, render_template
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from dotenv import load_dotenv
from discord import Permissions

load_dotenv()

app = Flask(__name__)

app.secret_key = b"%\xe0'\x01\xdeH\x8e\x85m|\xb3\xffCN\xc9g"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"    # !! Only in development environment.

app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI")

discord = DiscordOAuth2Session(app)


HYPERLINK = '<a href="{}">{}</a>'


@app.route("/")
def index():
    return render_template('home.html')


@app.route("/login/")
def login():
    return discord.create_session(scope=["identify", "guilds", "guilds.members.read"])


@app.route("/login-data/")
def login_with_data():
    return discord.create_session(data=dict(redirect="/me/", coupon="15off", number=15, zero=0, status=False))


# @app.route("/invite-bot/")
# def invite_bot():
#     return discord.create_session(scope=["bot"], permissions=8, guild_id=464488012328468480, disable_guild_select=True)


# @app.route("/invite-oauth/")
# def invite_oauth():
#     return discord.create_session(scope=["bot", "identify"], permissions=8)


@app.route("/callback/")
def callback():
    try:
        data = discord.callback()
        redirect_to = data.get("redirect", "/")
        
        # Ensure the token is saved
        token = discord.get_authorization_token()
        discord.save_authorization_token(token)
        
        # Fetch the user
        user = discord.fetch_user()
        
        return redirect(url_for("me"))  # Redirect to the /me endpoint
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return redirect(url_for("index"))


@app.route("/me/")
@requires_authorization
def me():
    try:
        user = discord.fetch_user()
        return render_template(
            'dashboard.html',
            user=user,
            avatar_url=user.avatar_url or user.default_avatar_url,
            username=user.name,
            user_id=user.id,
            is_avatar_animated=user.is_avatar_animated
        )
    except Exception as e:
        print(f"Error in /me route: {str(e)}")
        return redirect(url_for("index"))


@app.route("/me/guilds/")
@requires_authorization
def user_guilds():
    guilds = discord.fetch_guilds()
    return render_template('guild.html', guilds=guilds)


@app.route("/guild/<int:guild_id>/")
@requires_authorization
def guild_info(guild_id):
    user = discord.fetch_user()
    try:
        user_guilds = discord.fetch_guilds()
        guild = next((g for g in user_guilds if g.id == guild_id), None)
        
        if guild:
            member = discord.request(route=f'/users/@me/guilds/{guild.id}/member', method='GET')
            roles = [role['name'] for role in member.get('roles', [])]
            
            # Get the permission names
            permissions = guild.permissions
            permission_names = [perm for perm, value in permissions if value]
            
            # Check if the user is an admin
            is_admin = guild.permissions.administrator
            
            # Add some admin-only content
            admin_content = "This is secret admin information!" if is_admin else None
            
            return render_template('guild_info.html', 
                                   is_member=True,
                                   guild_name=guild.name,
                                   roles=roles,
                                   permissions=guild.permissions.value,
                                   permission_names=permission_names,
                                   is_admin=is_admin,
                                   admin_content=admin_content)
        else:
            return render_template('guild_info.html', 
                                   is_member=False,
                                   error="You are not a member of this guild")
    except Unauthorized:
        return render_template('guild_info.html', 
                               is_member=False,
                               error="Unauthorized to access this guild information")
    except Exception as e:
        return render_template('guild_info.html', 
                               is_member=False,
                               error=str(e))


@app.route("/logout/")
def logout():
    discord.revoke()
    return redirect(url_for(".index"))


@app.route("/secret/")
@requires_authorization
def secret():
    return os.urandom(16)


@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
