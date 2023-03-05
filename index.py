import traceback
import discord, sqlite3, os, random, asyncio, requests, datetime, json, time
from Setting import *
from discord_webhook import DiscordEmbed, DiscordWebhook
from discord_buttons_plugin import ButtonType
from discord_components import DiscordComponents, ComponentsBot, Select, SelectOption, Button, ButtonStyle, ActionRow

intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)

admin_id = 관리자
충전중=0
doing_bet = []

def get_kr_min():
    return datetime.datetime.now().strftime('%M')

def getinfo(id):
    url = f"https://discordapp.com/api/users/{id}"
    he = {
        "Authorization":f"Bot {MTA4MTgwMTc2NDkyOTUzNjAxMA.Gj4GFu.nVCIUqvYt6ioVX4027wPyB4xYYFIwO4aH6FGa8}"
    }
    res = requests.get(url,headers=he)
    r = res.json()
    return r

if not (os.path.isfile("./database/database.db ")):
    con = sqlite3.connect("./database/database.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE users (id INTEGER, money INTEGER, coin_bet_money INTEGER, ban INTEGER, perc INTEGER)")
    con.commit()
    con.close()


@client.event
async def on_ready():
    DiscordComponents(client)
    print(f"")
    print(f"─────────────────────────────────────────────────────")
    print(
        f"메인시스템을 실행 합니다.: {client.user}\n봇 초대 링크 : https://discord.com/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot")
    print(f"─────────────────────────────────────────────────────")
    print(f"사용 중인 서버 : {len(client.guilds)}개 관리 중")
    print(f"")


@client.event
async def on_message(message):

    if message.author.bot:
        return

    con = sqlite3.connect("./database/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
    user_info = cur.fetchone()

    if (user_info == None):
        cur.execute("INSERT INTO users Values(?, ?, ?, ?,?);", (
            message.author.id, 0, 0, 0, 0))
        con.commit()
        con.close()
    con.close()

    if (message.content == '!충전'):
        if message.author.id in admin_id:
            charge_embed=discord.Embed(title="충전 수단 선택",description="```yaml\n계좌, 문상 충전중 원하시는 버튼을 눌러주세요```",color=0x2f3136)
            account = Button(label="계좌충전", custom_id="계좌충전", style=ButtonStyle.blue)
            culture = Button(label="문상충전", custom_id="문상충전", style=ButtonStyle.red)
            await client.get_channel(충전채널).send(embed=charge_embed, components=
                        ActionRow(
                            [account, culture],
                        )
                                                    )
    if (message.content == '.코인'):
        if message.author.id in admin_id:
            not_come = 0
            min = int(get_kr_min()) % 3
            coin_embed = discord.Embed(title="3분에 한번씩 값이 변동됩니다.",
                                       description=f"```yaml\n코인매수 버튼을 눌러 원하는 금액을 투자해주세요.```",
                                       color=0x2f3136)
            coin = Button(label="코인매수", custom_id="코인투자", style=ButtonStyle.green)
            recall = Button(label="매도", custom_id="돈빼기", style=ButtonStyle.gray)
            coin_embed.set_footer(text=f'{3 - int(min)}분 남았습니다.')
            coin_msg = await client.get_channel(코인채널).send(embed=coin_embed, components=
            ActionRow(
                [coin,recall],
            )
                                                           )
            while True:
                min = int(get_kr_min()) % 3
                text=''
                if min==0:
                    if not_come==0:
                        not_come=1
                        for i in doing_bet:
                            con = sqlite3.connect("./database/database.db")
                            cur = con.cursor()
                            cur.execute("SELECT * FROM users WHERE id == ?;", (i,))
                            user_info = cur.fetchone()
                            user = client.get_user(i)
                            new_money = int(f'{round(user_info[2] * ((user_info[-1]/100)+1))}')
                            if new_money <= 100:
                                new_money=0
                                doing_bet.remove(i)
                            text += f"{user}: {user_info[2]}원 -> {new_money}원 {round(user_info[2]*(user_info[-1]/100))}원 {'🔺'if user_info[2]*(user_info[-1]/100)>0 else '🔽'}\n"
                            cur.execute("UPDATE users SET coin_bet_money = ? WHERE id == ?;",
                                        (new_money, i))
                            cur.execute("UPDATE users SET perc = ? WHERE id == ?;",
                                        (random.randint(-100, 100), i))
                            con.commit()
                            con.close()
                        if text=='':
                            coin_embed = discord.Embed(title="투자가 마감되었습니다.",
                                                       description=f"```yaml\n아무도 투자하지않았습니다.```",
                                                       color=0x2f3136)
                        else:
                            coin_embed = discord.Embed(title="투자가 마감되었습니다.",
                                                       description=f"```yaml\n{text}```",
                                                       color=0x2f3136)
                        await coin_msg.edit("@everyone", embed=coin_embed)
                    else:
                        await asyncio.sleep(30)
                elif min!=get_kr_min():
                    min = int(get_kr_min()) % 3
                    not_come=0
                    coin_embed = discord.Embed(title="3분에 한번씩 값이 변동됩니다.",
                                               description=f"```yaml\n코인매수 버튼을 눌러 원하는 금액을 투자해주세요.```",
                                               color=0x2f3136)
                    coin_embed.set_footer(text=f'{3 - int(min)}분 남았습니다.')
                    await coin_msg.edit("",embed=coin_embed)
    if message.content.startswith('!코인'):
        con = sqlite3.connect("./database/database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
        user_info = cur.fetchone()

        if (user_info == None):
            cur.execute("INSERT INTO users Values(?, ?, ?, ?,?);", (
                message.author.id, 0, 0, 0,0))
            con.commit()
            con.close()

        amsg = await message.channel.send("잠시만 기다려주세요..")
        conn = sqlite3.connect("./database/database.db")
        c = conn.cursor()
        list_all = list(c.execute("SELECT * FROM users"))
        list_all.sort(key=lambda x: -x[1])
        print()
        res_text = "=======투자액=======\n\n"
        idx = 0
        for ii in list_all:
            if ii[2] != 0:
                idx += 1
                res_text += str(idx) + ". " + str(await client.fetch_user(ii[0])) + " - " + str(ii[2]) + "원 투자중\n"

        conn.close()
        res_text = discord.Embed(title=f'유저 {idx}명의 투자내역입니다.',
                                 description=f'{res_text}',
                                 color=0x2f3136)
        await amsg.edit("", embed=res_text)



    if message.content.startswith('!순위'):
        con = sqlite3.connect("./database/database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id == ?;", (message.author.id,))
        user_info = cur.fetchone()

        if (user_info == None):
            cur.execute("INSERT INTO users Values(?, ?, ?, ?,?);", (
                message.author.id, 0, 0, 0,0))
            con.commit()
            con.close()
        try:
            args = message.content.split(" ")[1]
        except:
            args = ""

        amsg = await message.channel.send("잠시만 기다려주세요..")
        if (len(args) == 2):
            int(args).pop(0)
            counts = int(args[0])
            conn = sqlite3.connect("./database/database.db")
            c = conn.cursor()
            list_all = list(c.execute("SELECT * FROM users"))
            list_all.sort(key=lambda x: -x[1])
            print()
            res_text = "=======순위=======\n\n"
            idx = 1
            for ii in list_all[0:counts]:
                res_text += str(idx) + ". " + str(await client.fetch_user(ii[0])) + " - " + str(ii[1]) + "원 \n"
                idx += 1
            conn.close()
            # await amsg.edit(res_text)
            res_text = discord.Embed(title=f'유저 {counts}명의 순위입니다.',
                                     description=f'{res_text}',
                                     color=0x2f3136)
            await amsg.edit("", embed=res_text)


        else:
            conn = sqlite3.connect("./database/database.db")
            c = conn.cursor()
            list_all = list(c.execute("SELECT * FROM users"))
            list_all.sort(key=lambda x: -x[1])
            print()
            res_text = "=======순위=======\n\n"
            idx = 1
            for ii in list_all[0:10]:
                res_text += str(idx) + ". " + str(await client.fetch_user(ii[0])) + " - " + str(ii[1]) + "원 \n"
                idx += 1
            conn.close()
            res_text = discord.Embed(title='유저 10명의 순위입니다.',
                                     description=f'{res_text}',
                                     color=0x2f3136)
            await amsg.edit("", embed=res_text)

    if message.content.startswith('.정보'):
        try:
            m = message.content.split(" ")[1]
            m = m.split('@')[1]
            m = m.split('>')[0]
            id = int(m)
        except Exception as e:
            id = message.author.id
        con = sqlite3.connect("./database/database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id == ?;", (id,))
        user_info = cur.fetchone()

        if (user_info == None):
            cur.execute("INSERT INTO users Values(?, ?, ?, ?,?);", (
                message.author.id, 0, 0, 0,0))
            con.commit()
            con.close()

        con = sqlite3.connect("./database/database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id == ?;", (id,))
        user_info = cur.fetchone()

        if not (user_info == None):
            con.close()
            await message.channel.send(f"```py\n보유하신 머니 : {str(user_info[1])}원\n\n현재 매수액 : {str(user_info[2])}```")
        else:
            con.close()
            await message.channel.send("**```가입되있지않은 유저입니다.```**")

    if message.content.startswith('.강제충전 '):
        log_id = 입출금로그
        log_ch = client.get_channel(int(log_id))
        if message.author.id in admin_id:
            try:
                user_id = message.mentions[0].id
                amount = int(message.content.split(" ")[2])
            except:
                con.close()
                await message.channel.send("**```띄어쓰기 제대로 하세여.```**")
                return

            con = sqlite3.connect("./database/database.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
            user_info = cur.fetchone()

            if not (user_info == None):
                cur.execute("UPDATE users SET money = ? WHERE id == ?;", (user_info[1] + amount, user_id))

                con.commit()
                await message.channel.send(
                    f"```py\n{str(amount)}원 강제충전 성공\n\n{str(user_info[1])}원 -> {str(user_info[1] + amount)}원```")
                await log_ch.send(f"<@{message.mentions[0].id}>님이 {amount}원을 충전하셨습니다")
            else:
                con.close()
                await message.channel.send("**```가입되있지않은 유저입니다.```**")

    if message.content.startswith('.강제차감 '):
        if message.author.id in admin_id:
            try:
                user_id = message.mentions[0].id
                amount = int(message.content.split(" ")[2])
            except:
                con.close()
                await message.channel.send("**```띄어쓰기 제대로 하세여.```**")
                return

            con = sqlite3.connect("./database/database.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
            user_info = cur.fetchone()

            if not (user_info == None):
                cur.execute("UPDATE users SET money = ? WHERE id == ?;", (user_info[1] - amount, user_id))
                con.commit()
                await message.channel.send(
                    f"```py\n{str(amount)}원 강제차감 성공\n\n{str(user_info[1])}원 -> {str(user_info[1] - amount)}원```")
                res = getinfo(user_id)
                webhook = DiscordWebhook(
                    url=입출금로그웹훅,
                    username='환전로그',
                    avatar_url=f"https://cdn.discordapp.com/avatars/{user_id}/{res['avatar']}.webp?size=80",
                    content=f'<@{user_id}> 님이 {amount}원을 환전하셨습니다.')
                webhook.execute()
            else:
                con.close()
                await message.channel.send("**```가입되있지않은 유저입니다.```**")

    if message.content.startswith('!블랙리스트 '):
        if message.author.id in admin_id:
            user_id = message.mentions[0].id

            con = sqlite3.connect("./database/database.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
            user_info = cur.fetchone()

            if not (user_info == None):
                cur.execute("UPDATE users SET ban = ? WHERE id == ?;", (3, user_id))
                con.commit()
                con.close()
                await message.channel.send("**```성공적으로 블랙리스트 추가를 완료하였습니다!```**")
            else:
                con.close()
                await message.channel.send("**```가입되있지않은 유저입니다.```**")

    if message.content.startswith('!화이트리스트 '):
        if message.author.id in admin_id:
            user_id = message.mentions[0].id

            con = sqlite3.connect("./database/database.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
            user_info = cur.fetchone()

            if not (user_info == None):
                cur.execute("UPDATE users SET ban = ? WHERE id == ?;", (0, user_id))
                con.commit()
                con.close()
                await message.channel.send("**```성공적으로 화이트리스트 추가를 완료하였습니다!```**")
            else:
                con.close()
                await message.channel.send("**```가입되있지않은 유저입니다.```**")
    if message.content == '!명령어':
        if message.author.id in admin_id:
            embed = discord.Embed(title="명령어",
                                  description='**.코인**\n**```코인투자시스템을 시작합니다.```**\n**.강제차감 @유저 액수**\n**```유저를 원하는 액수만큼 차감합니다.```**\n**.강제충전 @유저 액수**\n**```유저를 원하는 액수만큼 충전합니다.```**\n**!블랙리스트 @유저\n**```유저를 블랙합니다.```**\n**!화이트리스트 @유저\n**```유저의 블랙을 해제합니다.```**',
                                  color=0x2f3136)
            embed.set_footer(text='할리코인 서비스')
        else:
            embed = discord.Embed(title="명령어",
                                  description='**.정보**\n**```가입 및 정보를 확인 합니다.```**\n**!순위**\n**```현재 순위를 봅니다```**\n**!코인**\n**```현재 유저들의 코인투자액을 봅니다.```**',
                                  color=0x2f3136)
            embed.set_footer(text='할리코인 서비스')
        await message.channel.send(embed=embed)

@client.event
async def on_button_click(interaction):
    global 충전중
    global doing_bet
    con = sqlite3.connect("./database/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
    user_info = cur.fetchone()

    if (user_info == None):
        cur.execute("INSERT INTO users Values(?, ?, ?, ?,?);", (
            interaction.user.id, 0, 0, 0, 0))
        con.commit()
        con.close()
    con.close()
    if interaction.custom_id == "코인투자":
        con = sqlite3.connect("./database/database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
        user_info = cur.fetchone()
        
        if not (user_info[3] == 3):
            if user_info[1] >= 1000:
                if not interaction.user.id in doing_bet:
                    doing_bet.append(interaction.user.id)
                    options = []
                    for i in range(1, (user_info[1] // 1000) + 1 if user_info[1] // 1000 < 24 else 25):
                        options.append(
                            SelectOption(description=f"",
                                         label=f"{1000 * i}", value=f"{1000 * i}"))
                    await interaction.respond(
                        embed=discord.Embed(title='금액 선택', description='매수할 금액을 선택해주세요.',
                                            color=0x0000FF)
                        ,
                        components=[
                            [Select(placeholder=f"매수액", options=options)]
                        ]
                    )
                else:
                    await interaction.respond(content="이미 매수중이십니다.")
                inter = await client.wait_for("select_option", check=None)
                amount = inter.values[0]
                cur.execute("UPDATE users SET money = ? WHERE id == ?;",
                            (user_info[1] - int(amount), interaction.user.id))
                con.commit()
                cur.execute("UPDATE users SET coin_bet_money = ? WHERE id == ?;",
                            (amount, interaction.user.id))
                con.commit()
                try:
                    await inter.respond(embed=discord.Embed(title="선택 성공",
                                                            description=f"{amount}원을 성공적으로 매수했습니다.",
                                                            color=0x2f3136))
                    cur.execute("UPDATE users SET perc = ? WHERE id == ?;",
                                (random.randint(-100,100), interaction.user.id))
                    con.commit()
                    con.close()
                except:
                    pass
            else:
                await interaction.respond(embed=discord.Embed(title="잔액부족",
                                                              description=f"잔고가 투자하기에 너무 낮습니다.", color=0x2f3136))
        else:
            await interaction.respond(embed=discord.Embed(title="매수불가",
                                                          description=f"당신은 차단된유저입니다.", color=0x2f3136))
    if interaction.custom_id == "돈빼기":
        try:
            con = sqlite3.connect("./database/database.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id == ?;", (interaction.user.id,))
            user_info = cur.fetchone()
            if not (user_info[3] == 3):
                await interaction.respond(content=f"> `{user_info[2]}`원을 성공적으로 회수하였습니다.\n> \n> {user_info[1]}원 -> {user_info[1]+user_info[2]}원")
                cur.execute("UPDATE users SET money = ? WHERE id == ?;",
                            (user_info[1]+user_info[2], interaction.user.id))
                con.commit()
                cur.execute("UPDATE users SET coin_bet_money = ? WHERE id == ?;",
                            (0, interaction.user.id))
                con.commit()
                con.close()
                doing_bet.remove(interaction.user.id)
            else:
                await interaction.respond(embed=discord.Embed(title="매도불가",
                                                            description=f"당신은 차단된유저입니다.", color=0x2f3136))
        except:
            await interaction.respond(embed=discord.Embed(title="매도불가",
                                                            description=f"당신은 배팅상태가아닙니다.", color=0x2f3136))










    if interaction.component.custom_id == "문상충전":
        if 충전중 == 0:
            충전중 = 1
            user_id = interaction.user.id
            print(interaction.user.name)

            con = sqlite3.connect("./database/database.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
            user_info = cur.fetchone()

            if (user_info == None):
                cur.execute("INSERT INTO users Values(?, ?, ?, ?,?);", (
                    user_id, 0, 0, 0,0))
                con.commit()
                con.close()

            con = sqlite3.connect("./database/database.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
            user_info = cur.fetchone()
            if not int(user_info[3]) >= 3:

                if not (user_info == None):
                    try:
                        await client.get_user(user_id).send("**```문화상품권 핀번호를 `-`를 포함해서 입력해주세요!```**")
                        await interaction.respond(content="**```DM을 확인해주세요```**")
                    except:
                        await interaction.respond(content="**```DM이 막혀있습니다```**")
                        충전중 = 0
                        print("충전끝")

                    def check(msg):
                        return (isinstance(msg.channel, discord.channel.DMChannel) and (
                                len(msg.content) == 21 or len(msg.content) == 19))

                    try:
                        munsang_pin = await client.wait_for("message", timeout=60, check=check)
                    except asyncio.TimeoutError:
                        try:
                            await client.get_user(user_id).send("**```\n시간이 초과되었습니다```**")
                            충전중 = 0
                            print("충전끝")
                        except:
                            pass
                        return None

                    try:
                        jsondata = {"pin": munsang_pin.content, "token": f"{api토큰}", "id": f"{컬쳐계정}",
                                    "pw": f"{컬쳐비번}"}
                        res = requests.post("http://59.13.7.199:123/api/charge", json=jsondata)
                        if (res.status_code != 200):
                            print(res)
                            raise TypeError
                        else:
                            print(str(res))
                            res = res.json()
                    except:
                        traceback.print_exc()
                        try:
                            await client.get_user(user_id).send("**```\n서버에 에러가 발생되었습니다```**")
                            충전중 = 0
                            print("충전끝")
                        except:
                            pass
                        return None

                    if (res["result"] == True):
                        amount = res["amount"]
                        con = sqlite3.connect("./database/database.db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
                        user_info = cur.fetchone()
                        now_money = int(user_info[1]) + amount
                        cur.execute("UPDATE users SET money = ? WHERE id == ?;", (now_money, user_id))
                        await client.get_user(user_id).send(f"**```\n{str(int(amount))}원 충전완료```**")
                        cur.execute("UPDATE users SET ban = ? WHERE id == ?;", (0, user_id))
                        con.commit()
                        con.close()
                        webhook = DiscordWebhook(
                            url=입출금로그웹훅,
                            content=f'<@{user_id}> 님이 {int(amount)}원을 충전하셨습니다.')
                        webhook.execute()
                        충전중 = 0
                        print(f"{munsang_pin.content} 충전끝")

                    elif (res["result"] == False):
                        con = sqlite3.connect("./database/database.db")
                        cur = con.cursor()
                        cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
                        user_info = cur.fetchone()

                        reason = res["reason"]
                        await client.get_user(user_id).send(f"```\n충전실패\n{reason}```")
                        cur.execute("UPDATE users SET ban = ? WHERE id == ?;", (int(user_info[3]) + 1, user_id))
                        con.commit()
                        con.close()
                        충전중 = 0
                        print("충전끝")
            else:
                await interaction.respond(
                    embed=discord.Embed(title="문화상품권 충전 실패", description=f"3회 연속 충전실패로 충전이 정지되었습니다.\n샵 관리자에게 문의해주세요.",
                                        color=0x2f3136))
                충전중 = 0
                print("충전끝")
        else:
            await interaction.respond(
                embed=discord.Embed(title="문화상품권 충전 실패", description=f"다른유저가 충전중입니다.\n버그 방지로 잠시후 충전해주세요.",
                                    color=0x2f3136))

    if interaction.component.custom_id == "계좌충전":
        user_id = interaction.user.id

        con = sqlite3.connect("./database/database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
        user_info = cur.fetchone()

        if (user_info == None):
            cur.execute("INSERT INTO users Values(?, ?, ?, ?,?);", (
                user_id, 0, 0, 0,0))
            con.commit()
            con.close()

        con = sqlite3.connect("./database/database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id == ?;", (user_id,))
        user_info = cur.fetchone()

        if not (user_info == None):
            try:
                nam = await interaction.user.send(embed=discord.Embed(description=f"```입금자명을 입력해주세요.```", color=0x2f3136))
                await interaction.respond(content="**```DM을 확인해주세요```**")
            except:
                await interaction.respond(content="**```DM이 막혀있습니다```**")

            def check(name):
                return (isinstance(name.channel, discord.channel.DMChannel) and (interaction.user.id == name.author.id))

            try:
                name = await client.wait_for("message", timeout=60, check=check)
                await nam.delete()
                name = name.content
            except asyncio.TimeoutError:
                try:
                    await interaction.user.send(embed=discord.Embed(title="계좌 충전 실패", description="```시간 초과되었습니다```", color=0x2f3136))
                except:
                    pass
                return None

            mone = await interaction.user.send(embed=discord.Embed(description=f"```입금할 액수를 입력해주세요.```", color=0x2f3136))

            def check(money):
                return (isinstance(money.channel, discord.channel.DMChannel) and (
                            interaction.user.id == money.author.id))

            try:
                money = await client.wait_for("message", timeout=60, check=check)
                await mone.delete()
                money = money.content
                if int(money) <1000:
                    await interaction.user.send(
                        embed=discord.Embed(title="계좌 충전 실패", description="```최소충전금은 1000원입니다.```", color=0x2f3136))
                    return None
            except asyncio.TimeoutError:
                try:
                    await interaction.user.send(
                        embed=discord.Embed(title="계좌 충전 실패", description="```시간 초과되었습니다.```", color=0x2f3136))
                except:
                    pass
                return None
            if money.isdigit():
                await interaction.user.send(embed=discord.Embed(title="계좌 충전",
                                                                description=f"**```py\n입금 계좌 : {계좌번호}```**\n─────────────\n입금자명 : `{name}`\n입금 금액 : `{money}`원",
                                                                color=0x2f3136))
                await interaction.user.send(
                    f"{계좌번호}")
                screenshot = await interaction.user.send(
                    embed=discord.Embed(description=f"```충전후 스크린샷을 5분내에 보내주세요.```", color=0x2f3136))

                def check(file):
                    return (isinstance(file.channel, discord.channel.DMChannel) and (
                            interaction.user.id == file.author.id))

                try:
                    file = await client.wait_for("message", timeout=300, check=check)
                    await screenshot.delete()
                    try:
                        if file.attachments != []:
                            for attach in file.attachments:
                                sct=attach.url
                    except:
                        try:
                            await interaction.user.send(
                                embed=discord.Embed(title="계좌 충전 실패", description="```올바른 사진 형식이 아닙니다.```",
                                                    color=0x2f3136))
                        except:
                            pass
                        return None
                except asyncio.TimeoutError:
                    try:
                        await interaction.user.send(
                            embed=discord.Embed(title="계좌 충전 실패", description="```시간 초과되었습니다.```", color=0x2f3136))
                    except:
                        pass
                    return None

                access_embed = discord.Embed(title='계좌이체 충전 요청',
                                             description=f'디스코드 닉네임 : <@{interaction.user.id}>({interaction.user})\n입금자명 : {name}\n입금금액 : {money}',
                                             color=0x2f3136)
                try:
                    access_embed.set_image(url=sct)
                except:
                    try:
                        await interaction.user.send(
                            embed=discord.Embed(title="계좌 충전 실패", description="```올바른 사진 형식이 아닙니다.```",
                                                color=0x2f3136))
                    except:
                        pass
                    return None
                await interaction.user.send(
                            embed=discord.Embed(title="충전 요청 성공 ✅", description=f"```yaml\n관리자의 승인을 기다려주세요.```",
                                                color=0x2f3136))
                access = Button(label="✅ 승인하기", custom_id="승인", style=ButtonStyle.green)
                deny = Button(label="❌ 거부하기", custom_id="거부", style=ButtonStyle.red)
                a_m = await client.get_channel(요청채널).send(embed=access_embed, components=
                ActionRow(
                    [access, deny],
                )
                                                          )
                while True:
                    interaction = await client.wait_for("button_click",
                                                        check=lambda inter: inter.custom_id != "",
                                                        timeout=None)
                    if interaction.custom_id == '승인':
                        await a_m.delete()
                        cur.execute("UPDATE users SET money = ? WHERE id == ?;",
                                    (user_info[1] + int(money), user_id))
                        con.commit()
                        con.close()
                        await client.get_user(user_id).send(embed=discord.Embed(title="계좌 충전 성공",
                                                                                description=f"{interaction.user} 관리자님께서 충전을 승인해주셨습니다. {money}원",
                                                                                color=0x2f3136))
                        await client.get_channel(요청채널).send(
                            embed=discord.Embed(title="계좌 충전 성공", description=f"<@{user_id}>님께 충전되었습니다. {money}원",
                                                color=0x2f3136))
                        log_id = 입출금로그
                        log_ch = client.get_channel(int(log_id))
                        await log_ch.send(f"<@{user_id}>님이 {int(money)}원을 충전하셨습니다")
                    if interaction.custom_id == '거부':
                        await a_m.delete()
                        await client.get_user(user_id).send(
                            embed=discord.Embed(title="계좌 충전 실패", description=f"{interaction.user} 관리자님께서 충전을 거부하셨습니다.",
                                                color=0x2f3136))
                        await client.get_channel(요청채널).send(
                            embed=discord.Embed(title="계좌 충전 실패", description=f"<@{user_id}>님의 계좌 충전이 거부되었습니다.",
                                                color=0x2f3136))

            else:
                await interaction.user.send(
                    embed=discord.Embed(title="계좌 충전 실패", description=f"```올바른 액수를 입력해주세요.```", color=0x2f3136))
client.run(봇토큰)
