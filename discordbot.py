import discord
from discord.ext.ui import View, Message, LinkButton, Button, MessageProvider, ViewTracker
from discord.ext import tasks
import requests
import urllib.parse
from datetime import datetime
from pytz import timezone

# botのアクセストークン
TOKEN = ''
# botの出力先チャンネルID
CHANNEL_ID = ''

# DiscordのサーバーID
GUILD_ID = ''

# UnbelievaBoatのアクセストークン
UNBELIEVABOAT_TOKEN = ''
# UnbelievaBoatのAPI(v1)のベースURL
UNBELIEVABOAT_BASE_URL = 'https://unbelievaboat.com/api/v1/'
# UnbelievaBoatのGet Balance APIのURL(/users/の後にユーザーIDをつける)
UNBELIEVABOAT_GETBALANCE_URL = UNBELIEVABOAT_BASE_URL + 'guilds/' + GUILD_ID + '/users/'

headers = {
    "accept": "application/json",
    "Authorization": UNBELIEVABOAT_TOKEN
}

# UnbelievaBoatの !money コマンド(Check your balance and leaderboard position)の返信メッセージの原型
# (key:author.proxy_icon_url はDiscord.pyにはないものだったので削除してある)
msg_balance = {'author': {'url': '', 'name': '', 'icon_url': ''}, 'fields': [{'value': '', 'name': 'Cash:', 'inline': True}, {'value': '', 'name': 'Bank:', 'inline': True}, {'value': '', 'name': 'Total:', 'inline': True}], 'color': 240116, 'type': 'rich', 'description': ''}


# copy from https://github.com/nkmk/python-snippets/notebook/urllib_parse_query_string.py
def remove_all_queries(url):
    return urllib.parse.urlunparse(urllib.parse.urlparse(url)._replace(query=None, fragment=None))

# copy from https://github.com/nkmk/python-snippets/notebook/urllib_parse_query_string.py
def update_query(url, key, new_val):
    pr = urllib.parse.urlparse(url)
    d = urllib.parse.parse_qs(pr.query)
    d[key] = new_val
    return urllib.parse.urlunparse(pr._replace(query=urllib.parse.urlencode(d, doseq=True)))

# 引数numに序数を連結した文字列を返す
# 考え方：
# one->first, two->second, three->third, four->fourth ...
# eleven->eleventh, twelve->twelfth, thirteen->thirteenth, fourteen->fourteenth ...
# twnty-one->twenty-first, twnty-two->twnty-second, twnty-three->twnty-third, twnty-four->twnty-fourth ...
#
# return   '1st' /   '2nd' /   '3rd' /   '4th' /.../
#         '11th' /  '12th' /  '13th' /  '14th' /.../
#         '21st' /  '22nd' /  '23rd' /  '24th' /.../
#        '111th' / '112th' / '113th' / '114th' /.../
#        '121st' / '122nd' / '123rd' / '124th' /.../
def int2ordinal(num):
	ordinal_dict = {1: 'st', 2: 'nd', 3: 'rd'}
	q, mod = divmod(num, 10)
	suffix = 'th'
	if mod in ordinal_dict:
		if q % 10 != 1:
			suffix = ordinal_dict[mod]
	return f'{num}{suffix}'



intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


class MyView(View):
	def __init__(self):
		super().__init__()

	async def money(self, interaction: discord.Interaction):
		response = requests.get(UNBELIEVABOAT_GETBALANCE_URL + str(interaction.user.id), headers=headers)
		response_json = response.json()
		# 返信用メッセージの作成
		msg_balance['author']['url'] = 'https://unbelievaboat.com/leaderboard/' + GUILD_ID + '/' + response_json['user_id']
		msg_balance['author']['name'] = interaction.user.display_name
		msg_balance['author']['icon_url'] = update_query(remove_all_queries(interaction.user.display_avatar.url), 'size', '128')
		msg_balance['fields'][0]['value'] = ':coin: ' + str(response_json['cash'])
		msg_balance['fields'][1]['value'] = ':coin: ' + str(response_json['bank'])
		msg_balance['fields'][2]['value'] = ':coin: ' + str(response_json['total'])
		msg_balance['description'] = 'Leaderboard Rank: ' + int2ordinal(int(response_json['rank']))
		print(msg_balance)
		msg_balance_embed = discord.Embed.from_dict(msg_balance)
		await interaction.message.channel.send(embed=msg_balance_embed)

	async def butachan(self, interaction: discord.Interaction):
		await interaction.message.channel.send(f'ﾌﾞﾋ(๑•🐽•๑)ﾌﾞﾋ')

#	async def delete(self, interaction: discord.Interaction):
#		await interaction.message.delete()
#		self.stop()

	async def body(self):
			return Message()\
			.content('ジルコインの数を確認しますか？')\
			.items([
				Button('確認したい')
					.on_click(self.money)
					.style(discord.ButtonStyle.primary),
				Button('ブヒ？')
					.on_click(self.butachan)
					.style(discord.ButtonStyle.secondary)
			]
		)

@client.event
async def on_ready():
	#now = datetime.now(timezone('Asia/Tokyo'))
	# 起動したらログイン通知を表示する
	#await client.get_channel(int(CHANNEL_ID)).send(f'We have logged in as {client.user}')
	# 定期実行のためのループ開始
	timeloop.start()

# 60秒ごとに呼び出される処理
@tasks.loop(seconds=60)
async def timeloop():
	now = datetime.now(timezone('Asia/Tokyo'))
	if now.hour == 0 and now.minute == 1:
		view = MyView()
		tracker = ViewTracker(view, timeout=None)
		await tracker.track(MessageProvider(client.get_channel(int(CHANNEL_ID))))

# botの起動とDiscordサーバーへの接続
client.run(TOKEN)
