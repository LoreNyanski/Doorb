from discord.ext.commands import Context, Bot

from src.pluginbot import sig_setup, resolve_dumbass

from .stats_schema import get_stat_item
from .stats_fetcher import fetch_leaderboard, fetch_stats
from .stats_renderer import render_leaderboard, render_stats

DEFAULT_LEADERBOARD = "count"

@sig_setup.connect
async def setup_commands(client: Bot):

    async def get_member(dumbass_id: int) -> str:
        user = client.get_user(dumbass_id)
        return user.name if user else f"User {dumbass_id}"

    @client.command()
    async def stats(ctx: Context, *args):
        """Lists all statistics for a set of people"""
        match len(args):
            case 0:
                # LIST ALL STATS FOR SELF
                entries = await fetch_stats([ctx.author.id])
                subject = ctx.author.name
            case 1:
                arg = str(args[0])
                if arg == "server" or arg == "guild":
                    # LIST ALL STATS FOR ONE GUILD
                    entries = await fetch_stats([user.id for user in ctx.guild.members])
                    subject = ctx.guild.name
                else:
                    # LIST STATS FOR MENTIONED PERSON
                    member = resolve_dumbass(ctx, arg)
                    if not member:
                        await ctx.send('Incorrect arguments loser (either mention someone or "server")')
                        return
                    entries = await fetch_stats([member.id])
                    subject = ctx.message.mentions[0].name
            case _:
                await ctx.send("Too many arguments bub")
                return
        result = await render_stats(entries, subject)
        await ctx.reply(content=result)

    @client.command()
    async def leaderboard(ctx: Context, *args):
        """Lists a ranking of all people for a specific statistic"""
        match len(args):
            case 0:
                stat_item = get_stat_item(DEFAULT_LEADERBOARD)
            case 1:
                stat_item = get_stat_item(args[0])
            case _:
                await ctx.send("Too many arguments bub")
                return
        if not stat_item:
            await ctx.send("thats not a real statistic ._.")
            return
        entries = await fetch_leaderboard([user.id for user in ctx.guild.members], stat_item)
        result = await render_leaderboard(entries, get_member)
        await ctx.send(content=result)