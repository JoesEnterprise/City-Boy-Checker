from config import *
from logic import *
import discord
from discord.ext import commands
from config import TOKEN

# Menginisiasi pengelola database
manager = DB_Map("database.db")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot started")

@bot.command()
async def start(ctx: commands.Context):
    await ctx.send(f"Halo, {ctx.author.name}. Masukkan !help_me untuk mengeksplorasi daftar perintah yang tersedia")

@bot.command()
async def help_me(ctx: commands.Context):
    help_text = """**📍 Bot Peta - Daftar Perintah:**
    
`!start` - Mulai bekerja dengan bot dan menerima pesan selamat datang.
`!help_me` - Menerima daftar perintah yang tersedia (perintah ini).
`!show_city <city_name>` - Menampilkan kota yang diberikan pada peta.
`!remember_city <city_name>` - Menyimpan kota yang diberikan ke daftar pribadi Anda.
`!show_my_cities` - Menampilkan semua kota yang telah Anda simpan pada peta.

**Contoh penggunaan:**
`!show_city Paris`
`!remember_city Tokyo`
`!show_my_cities`"""
    await ctx.send(help_text)

@bot.command()
async def show_city(ctx: commands.Context, *, city_name=""):
    if not city_name:
        await ctx.send("Penggunaan: `!show_city <city_name>`\nContoh: `!show_city Paris`")
        return
    
    # Check if city exists in database
    coords = manager.get_coordinates(city_name)
    if not coords:
        await ctx.send(f"Maaf, kota '{city_name}' tidak ditemukan dalam database.")
        return
    
    # Create map with the city
    map_path = f"map_{city_name.replace(' ', '_')}.png"
    manager.create_graph(map_path, [city_name])
    
    # Send the map as a file
    try:
        await ctx.send(f"Peta untuk kota **{city_name}**:", file=discord.File(map_path))
    except Exception as e:
        await ctx.send(f"Terjadi kesalahan saat menampilkan peta: {str(e)}")

@bot.command()
async def show_my_cities(ctx: commands.Context):
    cities = manager.select_cities(ctx.author.id)  # Mengambil daftar kota yang diingat oleh pengguna
    
    if not cities:
        await ctx.send("Anda belum menyimpan kota apapun. Gunakan `!remember_city <city_name>` untuk menyimpan kota.")
        return
    
    # Create map with all user's cities
    map_path = f"map_user_{ctx.author.id}.png"
    manager.create_graph(map_path, cities)
    
    # Send the map as a file
    try:
        cities_list = ", ".join(cities)
        await ctx.send(f"Peta dengan kota-kota Anda (**{cities_list}**):", file=discord.File(map_path))
    except Exception as e:
        await ctx.send(f"Terjadi kesalahan saat menampilkan peta: {str(e)}")

@bot.command()
async def remember_city(ctx: commands.Context, *, city_name=""):
    if manager.add_city(ctx.author.id, city_name):  # Memeriksa apakah kota ada dalam database; jika ya, menambahkannya ke memori pengguna
        await ctx.send(f'Kota {city_name} telah berhasil disimpan!')
    else:
        await ctx.send("Format tidak benar. Silakan masukkan nama kota dalam bahasa Inggris, dengan spasi setelah perintah.")

if __name__ == "__main__":
    bot.run(TOKEN)