# modal/view/embed
import discord

from app.bot_core import bot
from storage.storage import (
    load_subscriptions,
    save_subscriptions,
    encrypt_value,
)

# Consts
COOKIE_GUIDE_URL = "https://github.com/ecgregorio/resinly#finding-your-hoyolab-cookies"

### --- Modal Form --- ###
class SetupModal(discord.ui.Modal, title="Resinly Setup"):
    uid = discord.ui.TextInput(
        label="Genshin UID", 
        placeholder="Your 9-digit in-game UID",
        required=True, 
        max_length=9,
    )
    ltuid = discord.ui.TextInput(
        label="ltuid_v2", required=True,
        placeholder="Copy from your HoYoLab browser cookies",
    )
    ltoken = discord.ui.TextInput(
        label="ltoken_v2", required=True,
        placeholder="Copy from your HoYoLab browser cookies",
        style=discord.TextStyle.paragraph, # make it so the text doesn't cut off (too long cant see)
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        uid_value = str(self.uid).strip()
        # check if parameter values invalid
        if not uid_value.isdigit() or len(uid_value) != 9:
            await interaction.response.send_message(
                "UID must be exactly 9 digits.", ephemeral=True
            )
            return

        data = load_subscriptions()
        user_id = str(interaction.user.id)
        state = data.get(user_id, {})
        
        state["uid"] = uid_value
        state["ltuid_v2"] = encrypt_value(str(self.ltuid).strip())
        state["ltoken_v2"] = encrypt_value(str(self.ltoken).strip())
        state.setdefault("enabled", True)
        state.setdefault("notified_full", False)
        
        data[user_id] = state
        save_subscriptions(data)
        
        await interaction.response.send_message(
            "Setup saved securely. Notifications are enabled.",
            ephemeral=True,
        )

# help embed builder helper
def build_cookie_help_embed() -> discord.Embed:
    # create embed field
    embed = discord.Embed(
        title="How to find your HoYoLab cookies",
        description=(
            "You need two cookie values from your signed-in HoYoLab browser session: "
            "`ltuid_v2` and `ltoken_v2`"
        ),
        color=discord.Color.gold(),
    )
    
    # Chrome
    embed.add_field(
        name="Chrome / Edge",
        value=(
            "1. Sign in to HoYoLab in your browser. \n"
            "2. Open the HoYoLab site. \n"
            "3. Press `F12`. \n"
            "4. Open the `Application` tab (press `>>` or `+` if not seen). \n"
            "5. Open `Cookies` in the left sidebar. \n"
            "6. Select the HoYoLab site. \n"
            "7. Find `ltuid_v2` and `ltoken_v2` \n"
            "8. Copy their values into the setup form."
        ),
        inline=False,
    )
    
    # Firefox
    embed.add_field(
        name="Firefox",
        value=(
            "1. Sign in to HoYoLab in your browser. \n"
            "2. Press `F12`. \n"
            "3. Open the `Storage` tab. \n"
            "4. Open `Cookies` in the left sidebar. \n"
            "5. Select the HoYoLab site. \n"
            "6. Find `ltuid_v2` and `ltoken_v2` \n"
            "7. Copy their values into the setup form."
        ),
        inline=False,
    )
    
    # Safety
    embed.add_field(
        name="Safety",
        value=(
            "Treat these like passwords. Only submit them through Resinly's private setup flow. "
            "If you think they were exposed, log out of HoYoLab and sign back in."
        ),
        inline=False,
    )
     
    return embed

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(
            discord.ui.Button(
                label="Full Cookie Guide",
                style=discord.ButtonStyle.link,
                url=COOKIE_GUIDE_URL,
            )
        )
        
    @discord.ui.button(label="Open Secure Setup Form", style=discord.ButtonStyle.primary)
    async def open_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetupModal())
        
    @discord.ui.button(label="How to Find Cookies", style=discord.ButtonStyle.secondary)
    async def cookie_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=build_cookie_help_embed(),
            ephemeral=True,
        )

# setup slash command 
@bot.tree.command(name="setup", description="Securely set UID and HoYoLab cookies.")
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message(
        (
            "You'll need your 9-digit Genshin UID and two HoYoLab cookies: "
            "`ltuid_v2` and `ltoken_v2`.\n\n"
            "These are used only to read your Genshin notes and are stored encrypted. "
            "Use the help button if you don't know where to find them, or open the Full Cookie Guide on Github."
        ),
        view=SetupView(),
        ephemeral=True,
    )