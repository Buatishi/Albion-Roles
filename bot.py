import discord
import server
import os
from discord.ext import commands
from discord.ui import Select, View, Button


# Reemplaza con tu token de bot
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Configuración de los roles, con emojis representando cada rol
roles = {
    "MainTank": {"limit": 1, "emoji": "<:main_tank:1305226713675858050>"},
    "OffTank": {"limit": 1, "emoji": "<:off_tank:1305226744831410207>"},
    "GranArcano": {"limit": 1, "emoji": "<:gran_arcano:1305226907549433937>"},
    "Silence": {"limit": 1, "emoji": "<:silence:1305226870878507090>"},
    "Mainhealer": {"limit": 1, "emoji": "<:main_healer:1305630401632407692>"},
    "Ironroot": {"limit": 1, "emoji": "<:ironroot:1305226947600846998>"},
    "Shadowcaller": {"limit": 1, "emoji": "<:shadowcaller:1305226829002575874>"},
    "Lightcaller": {"limit": 1, "emoji": "<:lightcaller:1305227326623056042>"},
    "Ballesta": {"limit": 1, "emoji": "<:ballesta:1305627466231971933>"},
    "Frost": {"limit": 1, "emoji": "<:frost:1305226791941705778>"},
}

# Almacenamiento independiente por servidor y por comando para limpiar al ejecutarse nuevamente
server_user_roles = {}

def create_roles_embed(user_roles):
    embed = discord.Embed(title="Roles disponibles:", color=discord.Color.blue())
    roles_list = list(roles.keys())

    for i in range(0, len(roles_list), 3):
        roles_row = roles_list[i:i+3]
        roles_text = ""
        
        for role in roles_row:
            data = roles[role]
            assigned_users = user_roles.get(role, [])
            # Cambia a `display_name` para mostrar el apodo en el servidor
            user_list = ", ".join([user.display_name for user in assigned_users]) if assigned_users else "Nadie"
            roles_text += f"{data['emoji']} **{role}** ({len(assigned_users)}/{data['limit']})\n{user_list}\n\n"

        embed.add_field(name="\u200b", value=roles_text, inline=False)

    return embed

class RoleSelect(Select):
    def __init__(self, user_roles):
        self.user_roles = user_roles
        options = [
            discord.SelectOption(
                label=role,
                description=f"Selecciona el rol {role}",
                emoji=data['emoji']  # Añade el emoji aquí
            ) for role, data in roles.items()
        ]
        super().__init__(placeholder="Selecciona tu rol...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_role = self.values[0]
        current_role = next((r for r, users in self.user_roles.items() if interaction.user in users), None)

        # Remueve al usuario de su rol actual si existe
        if current_role:
            self.user_roles[current_role].remove(interaction.user)

        # Añade al usuario al nuevo rol seleccionado si hay espacio
        if interaction.user not in self.user_roles.get(selected_role, []):
            if len(self.user_roles.get(selected_role, [])) < roles[selected_role]["limit"]:
                self.user_roles.setdefault(selected_role, []).append(interaction.user)

        # Actualiza el embed y el mensaje
        new_embed = create_roles_embed(self.user_roles)
        await interaction.response.edit_message(embed=new_embed, view=self.view)

class UnregisterButton(Button):
    def __init__(self, user_roles):
        super().__init__(label="Desanotarse", style=discord.ButtonStyle.danger)
        self.user_roles = user_roles

    async def callback(self, interaction: discord.Interaction):
        # Remueve al usuario de cualquier rol al que esté anotado
        for role, users in self.user_roles.items():
            if interaction.user in users:
                users.remove(interaction.user)

        # Actualiza el embed y el mensaje
        new_embed = create_roles_embed(self.user_roles)
        await interaction.response.edit_message(embed=new_embed, view=self.view)

class RoleView(View):
    def __init__(self, user_roles):
        super().__init__(timeout=None)  # Sin límite de tiempo para la vista
        self.add_item(RoleSelect(user_roles))
        self.add_item(UnregisterButton(user_roles))  # Agrega el botón para desanotarse

@bot.command(name="roles")
async def roles_command(ctx):
    await ctx.message.delete()
    
    guild_id = ctx.guild.id

    # Reinicia los roles del servidor al ejecutar el comando nuevamente
    server_user_roles[guild_id] = {}

    user_roles = server_user_roles[guild_id]
    embed = create_roles_embed(user_roles)
    view = RoleView(user_roles)
    await ctx.send(embed=embed, view=view)


server.keep_alive()
bot.run(TOKEN)
