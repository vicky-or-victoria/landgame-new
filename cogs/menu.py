import discord
from discord.ext import commands
from utils.checks import is_owner
from utils import embeds
from db.queries.regions import get_player_regions, get_all_regions
from db.queries.players import get_player, get_all_players, get_leaderboard
from db.queries.military import get_armies
from db.queries.politics import get_research
from cogs.politics import RESEARCH_COSTS


async def post_public(bot, guild_id: int, content: str, embed: discord.Embed):
    channel_id = bot.config.get_channel(guild_id, "commands")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=content, embed=embed)


def main_menu_embed():
    e = embeds.info("Landgame — Command Center")
    e.description = (
        "Select a category to begin.\n\n"
        "Territory  — claim, develop, and build on regions\n"
        "Military   — raise and move armies, manage fronts\n"
        "Economy    — tax, trade, and the market\n"
        "Politics   — research and traditions\n"
        "Diplomacy  — treaties and war\n"
        "Info       — map, region inspection, leaderboard"
    )
    return e


class MainMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="My Status", style=discord.ButtonStyle.primary, custom_id="main:status", row=0)
    async def status(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        p = await get_player(interaction.client, interaction.guild_id, interaction.user.id)
        if not p:
            await interaction.followup.send(embed=embeds.error("Not Registered", "You are not a registered player."), ephemeral=True)
            return
        await interaction.followup.send(embed=embeds.player_status(p), ephemeral=True)

    @discord.ui.button(label="Territory", style=discord.ButtonStyle.secondary, custom_id="main:territory", row=1)
    async def territory(self, interaction, button):
        e = embeds.info("Territory")
        e.description = "Claim, develop, and construct buildings on your regions."
        await interaction.response.edit_message(embed=e, view=TerritoryView())

    @discord.ui.button(label="Military", style=discord.ButtonStyle.secondary, custom_id="main:military", row=1)
    async def military(self, interaction, button):
        e = embeds.info("Military")
        e.description = "Raise levies, move armies, and manage frontlines."
        await interaction.response.edit_message(embed=e, view=MilitaryView())

    @discord.ui.button(label="Economy", style=discord.ButtonStyle.secondary, custom_id="main:economy", row=1)
    async def economy(self, interaction, button):
        e = embeds.info("Economy")
        e.description = "Collect taxes, post market orders, and trade with other players."
        await interaction.response.edit_message(embed=e, view=EconomyView())

    @discord.ui.button(label="Politics", style=discord.ButtonStyle.secondary, custom_id="main:politics", row=2)
    async def politics(self, interaction, button):
        e = embeds.politics("Politics")
        e.description = "Unlock research and develop cultural traditions."
        await interaction.response.edit_message(embed=e, view=PoliticsView())

    @discord.ui.button(label="Diplomacy", style=discord.ButtonStyle.secondary, custom_id="main:diplomacy", row=2)
    async def diplomacy(self, interaction, button):
        e = embeds.info("Diplomacy")
        e.description = "Offer treaties, declare war, and view your active agreements."
        await interaction.response.edit_message(embed=e, view=DiplomacyView())

    @discord.ui.button(label="Info", style=discord.ButtonStyle.secondary, custom_id="main:info", row=2)
    async def info(self, interaction, button):
        e = embeds.info("Info")
        e.description = "View the map, inspect regions, and check the leaderboard."
        await interaction.response.edit_message(embed=e, view=InfoView())


class TerritoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Region", style=discord.ButtonStyle.secondary, custom_id="territory:claim")
    async def claim(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        regions = await get_all_regions(interaction.client, interaction.guild_id)
        unclaimed = [r for r in regions if not r["owner_id"]]
        if not unclaimed:
            await interaction.followup.send(embed=embeds.error("No Regions", "There are no unclaimed regions."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=r["name"], value=str(r["id"]), description=r["terrain"].capitalize())
            for r in unclaimed[:25]
        ]
        view = RegionSelectView(options, "claim_region", "Select a region to claim")
        await interaction.followup.send(embed=embeds.info("Claim Region", "Select a region to claim."), view=view, ephemeral=True)

    @discord.ui.button(label="Develop Region", style=discord.ButtonStyle.secondary, custom_id="territory:develop")
    async def develop(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        regions = await get_player_regions(interaction.client, interaction.guild_id, interaction.user.id)
        if not regions:
            await interaction.followup.send(embed=embeds.error("No Regions", "You do not own any regions."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=r["name"], value=str(r["id"]), description=f"{r['terrain'].capitalize()} — Dev {r['dev']}")
            for r in regions[:25]
        ]
        view = RegionSelectView(options, "develop_region", "Select a region to develop")
        await interaction.followup.send(embed=embeds.info("Develop Region", "Select a region to invest gold into."), view=view, ephemeral=True)

    @discord.ui.button(label="Build", style=discord.ButtonStyle.secondary, custom_id="territory:build")
    async def build(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        regions = await get_player_regions(interaction.client, interaction.guild_id, interaction.user.id)
        if not regions:
            await interaction.followup.send(embed=embeds.error("No Regions", "You do not own any regions."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=r["name"], value=str(r["id"]), description=r["terrain"].capitalize())
            for r in regions[:25]
        ]
        view = RegionSelectView(options, "build_region", "Select a region to build in")
        await interaction.followup.send(embed=embeds.info("Build", "Select a region to build in."), view=view, ephemeral=True)

    @discord.ui.button(label="Demolish", style=discord.ButtonStyle.secondary, custom_id="territory:demolish")
    async def demolish(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        regions = await get_player_regions(interaction.client, interaction.guild_id, interaction.user.id)
        if not regions:
            await interaction.followup.send(embed=embeds.error("No Regions", "You do not own any regions."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=r["name"], value=str(r["id"]), description=r["terrain"].capitalize())
            for r in regions[:25]
        ]
        view = RegionSelectView(options, "demolish_region", "Select a region to demolish from")
        await interaction.followup.send(embed=embeds.info("Demolish", "Select a region to remove a building from."), view=view, ephemeral=True)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.primary, custom_id="territory:back")
    async def back(self, interaction, button):
        await interaction.response.edit_message(embed=main_menu_embed(), view=MainMenuView())


class MilitaryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Raise Levy", style=discord.ButtonStyle.secondary, custom_id="military:raise")
    async def raise_levy(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        regions = await get_player_regions(interaction.client, interaction.guild_id, interaction.user.id)
        if not regions:
            await interaction.followup.send(embed=embeds.error("No Regions", "You do not own any regions."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=r["name"], value=str(r["id"]), description=f"Dev {r['dev']} — Levy cap {r['dev'] * 5}")
            for r in regions[:25]
        ]
        view = RegionSelectView(options, "raise_levy", "Select a region to raise a levy from")
        await interaction.followup.send(embed=embeds.info("Raise Levy", "Select a region to raise a levy from."), view=view, ephemeral=True)

    @discord.ui.button(label="Move Army", style=discord.ButtonStyle.secondary, custom_id="military:move")
    async def move(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        armies = await get_armies(interaction.client, interaction.guild_id, interaction.user.id)
        if not armies:
            await interaction.followup.send(embed=embeds.error("No Armies", "You have no armies."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=a["name"] or f"Army #{a['id']}", value=str(a["id"]), description=f"At {a.get('region_name', 'unknown')} — {a['size']} troops")
            for a in armies[:25]
        ]
        view = ArmySelectView(options, "move_army")
        await interaction.followup.send(embed=embeds.info("Move Army", "Select an army to move."), view=view, ephemeral=True)

    @discord.ui.button(label="Assign to Front", style=discord.ButtonStyle.secondary, custom_id="military:assign")
    async def assign(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        armies = await get_armies(interaction.client, interaction.guild_id, interaction.user.id)
        if not armies:
            await interaction.followup.send(embed=embeds.error("No Armies", "You have no armies."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=a["name"] or f"Army #{a['id']}", value=str(a["id"]), description=f"{a['size']} troops")
            for a in armies[:25]
        ]
        view = ArmySelectView(options, "assign_front")
        await interaction.followup.send(embed=embeds.info("Assign to Front", "Select an army to assign to a front."), view=view, ephemeral=True)

    @discord.ui.button(label="View Armies", style=discord.ButtonStyle.secondary, custom_id="military:view")
    async def view_armies(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        armies = await get_armies(interaction.client, interaction.guild_id, interaction.user.id)
        if not armies:
            await interaction.followup.send(embed=embeds.info("Armies", "You have no armies."), ephemeral=True)
            return
        lines = [f"{a['name'] or ('Army #' + str(a['id']))} — {a.get('region_name', 'unknown')} ({a['size']} troops)" for a in armies]
        await interaction.followup.send(embed=embeds.info("Your Armies", "\n".join(lines)), ephemeral=True)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.primary, custom_id="military:back")
    async def back(self, interaction, button):
        await interaction.response.edit_message(embed=main_menu_embed(), view=MainMenuView())


class EconomyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="View Balance", style=discord.ButtonStyle.secondary, custom_id="economy:balance")
    async def balance(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        p = await get_player(interaction.client, interaction.guild_id, interaction.user.id)
        if not p:
            await interaction.followup.send(embed=embeds.error("Not Registered", "You are not a registered player."), ephemeral=True)
            return
        await interaction.followup.send(embed=embeds.player_status(p), ephemeral=True)

    @discord.ui.button(label="Collect Tax", style=discord.ButtonStyle.secondary, custom_id="economy:tax")
    async def tax(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from db.queries.economy import collect_tax
        result = await collect_tax(interaction.client, interaction.guild_id, interaction.user.id)
        await interaction.followup.send(embed=embeds.success("Tax Collected", result), ephemeral=True)

    @discord.ui.button(label="Market", style=discord.ButtonStyle.secondary, custom_id="economy:market")
    async def market(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        resource_options = [
            discord.SelectOption(label="Gold",      value="gold"),
            discord.SelectOption(label="Food",      value="food"),
            discord.SelectOption(label="Materials", value="materials"),
        ]
        view = MarketResourceSelectView(resource_options)
        await interaction.followup.send(embed=embeds.info("Market", "Select a resource for your order."), view=view, ephemeral=True)

    @discord.ui.button(label="Trade", style=discord.ButtonStyle.secondary, custom_id="economy:trade")
    async def trade(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        players = await get_all_players(interaction.client, interaction.guild_id)
        others = [p for p in players if p["discord_id"] != interaction.user.id]
        if not others:
            await interaction.followup.send(embed=embeds.error("No Players", "There are no other players to trade with."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=p["name"], value=str(p["discord_id"]))
            for p in others[:25]
        ]
        view = PlayerSelectView(options, "trade")
        await interaction.followup.send(embed=embeds.info("Trade", "Select a player to trade with."), view=view, ephemeral=True)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.primary, custom_id="economy:back")
    async def back(self, interaction, button):
        await interaction.response.edit_message(embed=main_menu_embed(), view=MainMenuView())


class PoliticsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Research", style=discord.ButtonStyle.secondary, custom_id="politics:research")
    async def research(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        done = await get_research(interaction.client, interaction.guild_id, interaction.user.id)
        done_ids = {r["research_id"] for r in done}
        available = {k: v for k, v in RESEARCH_COSTS.items() if k not in done_ids}
        if not available:
            await interaction.followup.send(embed=embeds.politics("Research", "You have researched everything available."), ephemeral=True)
            return
        options = [
            discord.SelectOption(
                label=k.replace("_", " ").title(),
                value=k,
                description=f"Gold: {v.get('gold', 0)}  Influence: {v.get('influence', 0)}"
            )
            for k, v in available.items()
        ]
        view = ResearchSelectView(options)
        await interaction.followup.send(embed=embeds.politics("Research", "Select a technology to research."), view=view, ephemeral=True)

    @discord.ui.button(label="Traditions", style=discord.ButtonStyle.secondary, custom_id="politics:traditions")
    async def traditions(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from db.queries.politics import get_traditions
        t = await get_traditions(interaction.client, interaction.guild_id, interaction.user.id)
        lines = [tr["tradition_id"].replace("_", " ").title() for tr in t] if t else ["None unlocked yet."]
        await interaction.followup.send(embed=embeds.politics("Your Traditions", "\n".join(lines)), ephemeral=True)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.primary, custom_id="politics:back")
    async def back(self, interaction, button):
        await interaction.response.edit_message(embed=main_menu_embed(), view=MainMenuView())


class DiplomacyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Offer Treaty", style=discord.ButtonStyle.secondary, custom_id="diplomacy:offer")
    async def offer(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        players = await get_all_players(interaction.client, interaction.guild_id)
        others = [p for p in players if p["discord_id"] != interaction.user.id]
        if not others:
            await interaction.followup.send(embed=embeds.error("No Players", "There are no other players."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=p["name"], value=str(p["discord_id"]))
            for p in others[:25]
        ]
        view = PlayerSelectView(options, "offer_treaty")
        await interaction.followup.send(embed=embeds.info("Offer Treaty", "Select a player to offer a treaty to."), view=view, ephemeral=True)

    @discord.ui.button(label="Declare War", style=discord.ButtonStyle.danger, custom_id="diplomacy:war")
    async def war(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        players = await get_all_players(interaction.client, interaction.guild_id)
        others = [p for p in players if p["discord_id"] != interaction.user.id]
        if not others:
            await interaction.followup.send(embed=embeds.error("No Players", "There are no other players."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=p["name"], value=str(p["discord_id"]))
            for p in others[:25]
        ]
        view = PlayerSelectView(options, "declare_war")
        await interaction.followup.send(embed=embeds.warning("Declare War", "Select a player to declare war on."), view=view, ephemeral=True)

    @discord.ui.button(label="View Treaties", style=discord.ButtonStyle.secondary, custom_id="diplomacy:view")
    async def view_treaties(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from db.queries.diplomacy import get_treaties
        treaties = await get_treaties(interaction.client, interaction.guild_id, interaction.user.id)
        if not treaties:
            await interaction.followup.send(embed=embeds.info("Treaties", "No active treaties."), ephemeral=True)
            return
        lines = [f"{t['treaty_type'].title()} with {t['other']} — {t['status']}" for t in treaties]
        await interaction.followup.send(embed=embeds.info("Your Treaties", "\n".join(lines)), ephemeral=True)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.primary, custom_id="diplomacy:back")
    async def back(self, interaction, button):
        await interaction.response.edit_message(embed=main_menu_embed(), view=MainMenuView())


class InfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="View Map", style=discord.ButtonStyle.secondary, custom_id="info:map")
    async def view_map(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from renderer.map_renderer import render_map
        img = await render_map(interaction.client, interaction.guild_id)
        await interaction.followup.send(file=img, ephemeral=True)

    @discord.ui.button(label="Inspect Region", style=discord.ButtonStyle.secondary, custom_id="info:inspect_region")
    async def inspect_region(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        regions = await get_all_regions(interaction.client, interaction.guild_id)
        if not regions:
            await interaction.followup.send(embed=embeds.error("No Regions", "No regions exist yet."), ephemeral=True)
            return
        options = [
            discord.SelectOption(label=r["name"], value=str(r["id"]), description=r["terrain"].capitalize())
            for r in regions[:25]
        ]
        view = RegionSelectView(options, "inspect_region", "Select a region to inspect")
        await interaction.followup.send(embed=embeds.info("Inspect Region", "Select a region to inspect."), view=view, ephemeral=True)

    @discord.ui.button(label="Leaderboard", style=discord.ButtonStyle.secondary, custom_id="info:leaderboard")
    async def leaderboard(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        rows = await get_leaderboard(interaction.client, interaction.guild_id)
        lines = [f"{i+1}. {r['name']} — {r['prestige']} prestige" for i, r in enumerate(rows)]
        await interaction.followup.send(embed=embeds.info("Leaderboard", "\n".join(lines) if lines else "No players yet."), ephemeral=True)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.primary, custom_id="info:back")
    async def back(self, interaction, button):
        await interaction.response.edit_message(embed=main_menu_embed(), view=MainMenuView())


class RegionSelectView(discord.ui.View):
    def __init__(self, options, action: str, placeholder: str):
        super().__init__(timeout=60)
        self.action = action
        select = discord.ui.Select(placeholder=placeholder, options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        region_id = int(interaction.data["values"][0])
        if self.action == "claim_region":
            from cogs.territory import handle_claim
            await handle_claim(interaction, region_id)
        elif self.action == "develop_region":
            await interaction.response.send_modal(AmountModal("Develop Region", "Gold to invest (e.g. 100)", "develop", region_id))
        elif self.action == "build_region":
            from db.queries.buildings import BUILDING_DEFINITIONS
            options = [
                discord.SelectOption(label=k.title(), value=k, description=f"Tier {v['tier']} — {v['category'].title()}")
                for k, v in BUILDING_DEFINITIONS.items()
            ]
            view = BuildingSelectView(options, region_id, "build")
            await interaction.response.edit_message(embed=embeds.info("Build", "Select a building to construct."), view=view)
        elif self.action == "demolish_region":
            from db.queries.buildings import get_buildings
            buildings = await get_buildings(interaction.client, interaction.guild_id, region_id)
            if not buildings:
                await interaction.response.edit_message(embed=embeds.error("No Buildings", "That region has no buildings."), view=None)
                return
            options = [
                discord.SelectOption(label=b["name"], value=b["name"].lower(), description=f"Tier {b['tier']}")
                for b in buildings[:25]
            ]
            view = BuildingSelectView(options, region_id, "demolish")
            await interaction.response.edit_message(embed=embeds.info("Demolish", "Select a building to demolish."), view=view)
        elif self.action == "raise_levy":
            from cogs.military import handle_raise_levy
            await handle_raise_levy(interaction, region_id)
        elif self.action == "inspect_region":
            from cogs.info import handle_inspect_region
            await handle_inspect_region(interaction, region_id)


class ArmySelectView(discord.ui.View):
    def __init__(self, options, action: str):
        super().__init__(timeout=60)
        self.action = action
        select = discord.ui.Select(placeholder="Select an army", options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        army_id = int(interaction.data["values"][0])
        if self.action == "move_army":
            regions = await get_all_regions(interaction.client, interaction.guild_id)
            options = [
                discord.SelectOption(label=r["name"], value=str(r["id"]), description=r["terrain"].capitalize())
                for r in regions[:25]
            ]
            view = RegionForArmyView(options, army_id, "move_army")
            await interaction.response.edit_message(embed=embeds.info("Move Army", "Select a destination region."), view=view)
        elif self.action == "assign_front":
            regions = await get_all_regions(interaction.client, interaction.guild_id)
            options = [
                discord.SelectOption(label=r["name"], value=str(r["id"]), description=r["terrain"].capitalize())
                for r in regions[:25]
            ]
            view = RegionForArmyView(options, army_id, "assign_front")
            await interaction.response.edit_message(embed=embeds.info("Assign to Front", "Select a frontline region."), view=view)


class RegionForArmyView(discord.ui.View):
    def __init__(self, options, army_id: int, action: str):
        super().__init__(timeout=60)
        self.army_id = army_id
        self.action  = action
        select = discord.ui.Select(placeholder="Select a region", options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        region_id = int(interaction.data["values"][0])
        if self.action == "move_army":
            from cogs.military import handle_move_army
            await handle_move_army(interaction, self.army_id, region_id)
        elif self.action == "assign_front":
            from cogs.military import handle_assign_front
            await handle_assign_front(interaction, self.army_id, region_id)


class BuildingSelectView(discord.ui.View):
    def __init__(self, options, region_id: int, action: str):
        super().__init__(timeout=60)
        self.region_id = region_id
        self.action    = action
        select = discord.ui.Select(placeholder="Select a building", options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        building_name = interaction.data["values"][0]
        if self.action == "build":
            from cogs.territory import handle_build
            await handle_build(interaction, self.region_id, building_name)
        elif self.action == "demolish":
            from cogs.territory import handle_demolish
            await handle_demolish(interaction, self.region_id, building_name)


class PlayerSelectView(discord.ui.View):
    def __init__(self, options, action: str):
        super().__init__(timeout=60)
        self.action = action
        select = discord.ui.Select(placeholder="Select a player", options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        target_id = int(interaction.data["values"][0])
        if self.action == "trade":
            resource_options = [
                discord.SelectOption(label="Gold",      value="gold"),
                discord.SelectOption(label="Food",      value="food"),
                discord.SelectOption(label="Materials", value="materials"),
            ]
            view = TradeResourceSelectView(resource_options, target_id)
            await interaction.response.edit_message(embed=embeds.info("Trade", "Select a resource to send."), view=view)
        elif self.action == "offer_treaty":
            treaty_options = [
                discord.SelectOption(label="Alliance", value="alliance"),
                discord.SelectOption(label="Non-Aggression Pact", value="nap"),
                discord.SelectOption(label="Trade Agreement", value="trade"),
            ]
            view = TreatyTypeSelectView(treaty_options, target_id)
            await interaction.response.edit_message(embed=embeds.info("Offer Treaty", "Select a treaty type."), view=view)
        elif self.action == "declare_war":
            from cogs.diplomacy import handle_declare_war
            await handle_declare_war(interaction, target_id)


class TreatyTypeSelectView(discord.ui.View):
    def __init__(self, options, target_id: int):
        super().__init__(timeout=60)
        self.target_id = target_id
        select = discord.ui.Select(placeholder="Select a treaty type", options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        treaty_type = interaction.data["values"][0]
        from cogs.diplomacy import handle_offer_treaty
        await handle_offer_treaty(interaction, self.target_id, treaty_type)


class TradeResourceSelectView(discord.ui.View):
    def __init__(self, options, target_id: int):
        super().__init__(timeout=60)
        self.target_id = target_id
        select = discord.ui.Select(placeholder="Select a resource", options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        resource = interaction.data["values"][0]
        await interaction.response.send_modal(TradeAmountModal(resource, self.target_id))


class MarketResourceSelectView(discord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=60)
        select = discord.ui.Select(placeholder="Select a resource", options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        resource = interaction.data["values"][0]
        order_options = [
            discord.SelectOption(label="Buy",  value="buy"),
            discord.SelectOption(label="Sell", value="sell"),
        ]
        view = MarketOrderTypeView(order_options, resource)
        await interaction.response.edit_message(embed=embeds.info("Market", "Select order type."), view=view)


class MarketOrderTypeView(discord.ui.View):
    def __init__(self, options, resource: str):
        super().__init__(timeout=60)
        self.resource = resource
        select = discord.ui.Select(placeholder="Select order type", options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        order_type = interaction.data["values"][0]
        await interaction.response.send_modal(MarketAmountModal(self.resource, order_type))


class ResearchSelectView(discord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=60)
        select = discord.ui.Select(placeholder="Select research", options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        research_id = interaction.data["values"][0]
        from cogs.politics import handle_research
        await handle_research(interaction, research_id)


class AmountModal(discord.ui.Modal):
    def __init__(self, title: str, placeholder: str, action: str, region_id: int):
        super().__init__(title=title)
        self.action    = action
        self.region_id = region_id
        self.amount_input = discord.ui.TextInput(
            label="Amount (gold)",
            placeholder=placeholder,
            min_length=1,
            max_length=7
        )
        self.add_item(self.amount_input)

    async def on_submit(self, interaction: discord.Interaction):
        amount = int(self.amount_input.value)
        if self.action == "develop":
            from cogs.territory import handle_develop
            await handle_develop(interaction, self.region_id, amount)


class TradeAmountModal(discord.ui.Modal, title="Trade"):
    def __init__(self, resource: str, target_id: int):
        super().__init__(title=f"Send {resource.title()}")
        self.resource  = resource
        self.target_id = target_id
        self.amount_input = discord.ui.TextInput(
            label="Amount",
            placeholder="Enter amount to send (e.g. 100)",
            min_length=1,
            max_length=7
        )
        self.add_item(self.amount_input)

    async def on_submit(self, interaction: discord.Interaction):
        amount = int(self.amount_input.value)
        from cogs.economy import handle_trade
        await handle_trade(interaction, self.target_id, self.resource, amount)


class MarketAmountModal(discord.ui.Modal):
    def __init__(self, resource: str, order_type: str):
        super().__init__(title=f"Market — {order_type.title()} {resource.title()}")
        self.resource   = resource
        self.order_type = order_type
        self.amount_input = discord.ui.TextInput(
            label="Amount",
            placeholder="How many units (e.g. 50)",
            min_length=1,
            max_length=7
        )
        self.price_input = discord.ui.TextInput(
            label="Price per unit (gold)",
            placeholder="Price per unit (e.g. 5)",
            min_length=1,
            max_length=6
        )
        self.add_item(self.amount_input)
        self.add_item(self.price_input)

    async def on_submit(self, interaction: discord.Interaction):
        amount = int(self.amount_input.value)
        price  = int(self.price_input.value)
        from cogs.economy import handle_market_order
        await handle_market_order(interaction, self.resource, amount, price, self.order_type)


class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(MainMenuView())
        bot.add_view(TerritoryView())
        bot.add_view(MilitaryView())
        bot.add_view(EconomyView())
        bot.add_view(PoliticsView())
        bot.add_view(DiplomacyView())
        bot.add_view(InfoView())

    @discord.app_commands.command(name="deploy_menu", description="Post the persistent menu to #menu")
    @is_owner()
    async def deploy_menu(self, interaction: discord.Interaction):
        cfg = self.bot.config
        channel_id = cfg.get_channel(interaction.guild_id, "menu")
        if not channel_id:
            await interaction.response.send_message(embed=embeds.error("Menu channel not set."), ephemeral=True)
            return
        channel = self.bot.get_channel(channel_id)
        msg = await channel.send(embed=main_menu_embed(), view=MainMenuView())
        cfg.set_menu_message(interaction.guild_id, msg.id)
        await interaction.response.send_message(embed=embeds.success("Menu deployed."), ephemeral=True)


async def setup(bot):
    await bot.add_cog(Menu(bot))
