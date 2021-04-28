import discord
from discord.ext import commands
import json
import os
from boto.s3.connection import S3Connection

client = commands.Bot(command_prefix="!")


with open("data.json", "r") as f:
    data = json.load(f)


@client.event
async def on_ready():
    print("Bot running with:")
    print("Username: ", client.user.name)
    print("User ID: ", client.user.id)


@client.event
async def on_reaction_add(reaction, user):
    print(reaction.emoji)
    if user.id == client.user.id:
        print("bot")
        return
    if reaction.emoji == "📖" and reaction.message.id in data["idMessagesToOpenTicket"]:
        await reaction.remove(user)
        category = client.get_channel(data["categoryId"])
        channel = await category.create_text_channel("ticket {}".format(data["count"]))
        em = discord.Embed(
            title="Open a Ticket", description="Tell us your problem", color=0x5a6b7e)
        em.set_footer(
            text="SquareFNF Tickets (!close to close ticket)", icon_url="https://cdn.discordapp.com/attachments/836621530124255233/836707131423064114/logo.png")
        await channel.send(embed=em)
        a = await channel.send(channel.guild.roles[0])
        await a.delete()
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        overwrite.read_messages = True
        await channel.set_permissions(user, overwrite=overwrite)
        data["tickets"].append(channel.id)
        data["count"] += 1
        with open("data.json", "w") as f:
            json.dump(data, f)


@client.command()
@commands.has_permissions(administrator=True)
async def setChannel(ctx, args):
    try:
        channel = client.get_channel(int(args))
        em = discord.Embed(
            title="Open a Ticket", description="React here to open a ticket", color=0x5a6b7e)
        em.set_footer(
            text="SquareFNF Tickets", icon_url="https://cdn.discordapp.com/attachments/836621530124255233/836707131423064114/logo.png")
        message = await channel.send(embed=em)
        await message.add_reaction("📖")
        messageId = message.id
        data["idMessagesToOpenTicket"].append(messageId)
        data["count"] += 1
        with open("data.json", "w") as f:
            json.dump(data, f)

        em = discord.Embed(title="SquareFNF Tickets",
                           description="A ticket message has been set.", color=0x5a6b7e)

        await ctx.send(embed=em)
    except Exception as e:
        print(e)
        em = discord.Embed(title="SquareFNF Tickets",
                           description="This id is not valid. ", color=0x5a6b7e)

        await ctx.send(embed=em)


@client.command()
@commands.has_permissions(administrator=True)
async def setCategory(ctx, args):
    try:
        channel = client.get_channel(int(args))
        if channel == None:
            em = discord.Embed(title="SquareFNF Tickets",
                               description="This id is not valid. ", color=0x5a6b7e)

            await ctx.send(embed=em)
        else:
            if data["role"] == 0:
                role = await ctx.guild.create_role(name="Support Team")
                overwrite = discord.PermissionOverwrite()
                overwrite.send_messages = True
                overwrite.read_messages = True
                await channel.set_permissions(role, overwrite=overwrite)
            data["categoryId"] = int(args)
            with open("data.json", "w") as f:
                json.dump(data, f)
            em = discord.Embed(title="SquareFNF Tickets",
                               description="The category is set", color=0x5a6b7e)

            await ctx.send(embed=em)
    except Exception as e:
        print(e)
        em = discord.Embed(title="SquareFNF Tickets",
                           description="This id is not valid. ", color=0x5a6b7e)

        await ctx.send(embed=em)


@client.command()
async def close(ctx):
    if ctx.channel.id in data["tickets"]:
        channel = client.get_channel(ctx.channel.id)
        await channel.delete()
        del data["tickets"][data["tickets"].index(ctx.channel.id)]


@client.command()
@commands.has_permissions(administrator=True)
async def addSupport(ctx, member: discord.Member):
    if member.id in data["allowedMember"]:
        em = discord.Embed(title="SquareFNF Tickets",
                           description="This member is already in the support team.", color=0x5a6b7e)

        await ctx.send(embed=em)
    else:
        role = discord.utils.get(member.guild.roles, name="Support Team")
        await member.add_roles(role)
        data["allowedMember"].append(member.id)
        channel = client.get_channel(data["categoryId"])
        with open("data.json", "w") as f:
            json.dump(data, f)
        em = discord.Embed(title="SquareFNF Tickets",
                           description="<@{}> joined the support team.".format(member.id), color=0x5a6b7e)
        await ctx.send(embed=em)


@client.command()
@commands.has_permissions(administrator=True)
async def delSupport(ctx, member: discord.Member):
    if member.id not in data["allowedMember"]:
        em = discord.Embed(title="SquareFNF Tickets",
                           description="This member is not in the support team.", color=0x5a6b7e)

        await ctx.send(embed=em)
    else:
        role = discord.utils.get(member.guild.roles, name="Support Team")
        await member.remove_roles(role)
        del data["allowedMember"][data["allowedMember"].index(member.id)]
        with open("data.json", "w") as f:
            json.dump(data, f)
        channel = client.get_channel(data["categoryId"])
        em = discord.Embed(title="SquareFNF Tickets",
                           description="<@{}> quitted the support team.".format(member.id), color=0x5a6b7e)
        await ctx.send(embed=em)


@addSupport.error
async def addrole_error(ctx, error):
    print(error)
    em = discord.Embed(title="SquareFNF Tickets",
                       description="Error", color=0x5a6b7e)
    await ctx.send(embed=em)

token = S3Connection(os.environ['TOKEN'])
client.run(token)
