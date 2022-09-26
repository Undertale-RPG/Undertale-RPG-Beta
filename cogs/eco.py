import random
from xml.etree.ElementTree import tostring
from disnake.ext import commands
import disnake
from utility.utils import create_player_info
import time

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Get your supporter reward for being in our support server")
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def supporter(self, inter):
        if inter.guild.id != 992432202002468895:
            return await inter.send(
                "this command is exclusive for our support server, you can join via \n\n https://discord.gg/FQYVpuNz4Q"
            )
        
        author = inter.author

        info = await self.bot.players.find_one({"_id": author.id})
        goldget = random.randint(500, 1000) * info["multi_g"]
        try:
            curr_time = time.time()
            delta = int(curr_time) - int(info["supporter_block"])

            if delta >= 86400 and delta > 0:
                info["gold"] += goldget
                info["supporter_block"] = curr_time
                await self.bot.players.update_one(
                    {"_id": author.id}, {"$set": info}
                )
                em = disnake.Embed(
                    description=f"**You received your supporter gold! {int(goldget)} G**",
                    color=0x0077ff,
                )
            else:
                seconds = 86400 - delta
                em = disnake.Embed(
                    description=(
                        f"**You can't claim your supporter reward yet!\n\n You can use this command again"
                        f" <t:{int(time.time()) + int(seconds)}:R>**"
                        ),
                    color=0x0077ff,
                    )
            await inter.send(embed=em)
        except KeyError:
            info["supporter_block"] = 0
            await self.bot.players.update_one({"_id": author.id}, {"$set": info})

    @commands.slash_command()
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def stats(self, inter):
        """Check your stats and progress"""
        player = inter.author
        if player.bot:
            await inter.send("Nice try!")
            return
        data = await inter.bot.players.find_one({"_id": inter.author.id})

        health = data["health"]
        love = data["level"]
        exp = data["exp"]
        kills = data["kills"]
        deaths = data["deaths"]
        weapon = data["weapon"]
        armor = data["armor"]
        gold = data["gold"]
        resets = data["resets"]
        multi_g = data["multi_g"] 
        multi_xp = data["multi_xp"]

        em = disnake.Embed(
            title = f"{player}'s stats",
            color = 0x0077ff,
            description = "Your Status and progress in the game"
        )
        em.set_thumbnail(url=player.display_avatar)
        em.add_field(name="▫️┃Health", value=f"{round(health)}")
        em.add_field(name="▫️┃LOVE", value=f"{round(love)}")
        em.add_field(name="▫️┃EXP", value=f"{round(exp)}")
        em.add_field(name="▫️┃Kills", value=f"{round(kills)}")
        em.add_field(name="▫️┃Deaths", value=f"{round(deaths)}")
        em.add_field(name="▫️┃Weapon", value=f"{weapon}")
        em.add_field(name="▫️┃Armor", value=f"{armor}")
        em.add_field(name="▫️┃Gold", value=f"{round(gold)}")
        em.add_field(name="▫️┃resets", value=f"{round(resets)}")
        em.add_field(name="▫️┃Gold Multiplier", value=f"{round(multi_g)}")
        em.add_field(name="▫️┃EXP Multiplier", value=f"{round(multi_xp)}")

        await inter.send(inter.author.mention, embed=em)

    @commands.slash_command()
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def booster(self, inter):
        """Claim Your daily booster Reward!"""
        author = inter.author
        data = await self.bot.players.find_one({"_id": author.id})
        boosters = await self.bot.db["boosters"].find_one({"_id": 0})
        await create_player_info(inter, inter.author)

        if author.id not in boosters["boosters"]:
            await inter.send(
                "You are not a booster!, only people who boost our support server are able to get the rewards!")
            return
       
        new_gold = 2500 * data["multi_g"]
        curr_time = time.time()
        delta = int(curr_time) - int(int(data["booster_block"]))

        if delta >= 86400:
            data["gold"] += new_gold
            data["booster_block"]= curr_time
            await self.bot.players.update_one({"_id": author.id}, {"$set": data})
            await inter.send(f"**You recieved your booster gold! {int(new_gold)} G**")
        else:
            seconds = 86400 - delta
            em = disnake.Embed(
                description=(
                    f"**You can't claim your booster reward yet!\n\nYou can claim your booster reward"
                    f" <t:{int(time.time()) + int(seconds)}:R>**"),
                color=0x0077ff,
            )

            await inter.send(embed=em)

    @commands.slash_command(description="Claim your daily gold reward")
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def daily(self, inter):
        data = await self.bot.players.find_one({"_id": inter.author.id})

        new_gold = 500 * data["multi_g"]
        curr_time = time.time()
        delta = int(curr_time) - int(int(data["daily_block"]))

        if delta >= 86400:
            data["gold"] += new_gold
            data["daily_block"] = curr_time
            await self.bot.players.update_one({"_id": inter.author.id}, {"$set": data})
            await inter.send(f"**You recieved your daily gold! {int(new_gold)} G**")
        else:
            seconds = 86400 - delta
            em = disnake.Embed(
                description=(
                    f"**You can't claim your daily reward yet!\n\nYou can claim your daily reward"
                    f" <t:{int(time.time()) + int(seconds)}:R>**"),
                color=0x0077ff
            )
            await inter.send(embed=em)

def setup(bot):
    bot.add_cog(Economy(bot))