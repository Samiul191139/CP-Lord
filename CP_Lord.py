import discord
from discord.ext import tasks, commands
from discord import ui
from datetime import datetime, timezone
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import json
import os
from dotenv import load_dotenv


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CONFIG_FILE = "server_config.json"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

server_config = {}

def load_config():
    """Load configurations from a JSON file."""
    global server_config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            server_config = json.load(f)

def save_config():
    """Save current configurations to a JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(server_config, f, indent=4)

# Load existing configurations at the start
load_config()

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user}')
    await bot.tree.sync()  # Sync the slash commands globally
    check_for_contests.start()  # Start background task

@bot.event
async def on_guild_join(guild):
    """Event handler for when the bot joins a new server."""
    # Get a default text channel to send the setup message
    default_channel = None
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            default_channel = channel
            break

    if default_channel:
        # Send setup instructions to a default channel
        await default_channel.send(
            f"Hello There! I am CP_Lord, your personal Competetive Programming Contest Finder. Thanks for adding me to {guild.name}.\n"
            "Please use the `/codeforces` command to find the upcoming contests from Codeforces.\n"
            "Please use the `/all_contest` command to find all the upcoming contests from all popular CP websites.\n"
            "HAPPY CODING !!!"
        )
    else:
        print(f"Could not send setup instructions to {guild.name} - no accessible channels.")


async def scrape_contests():
    """Fetch upcoming contests from the first URL."""
    contests = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://contestmania.web.app/codeforces?category=All")
        await page.wait_for_timeout(5000)  # Wait for JavaScript to load the content

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        upcoming_elements = soup.find_all('td', class_='bg-notattempted', string='Upcoming')

        for element in upcoming_elements:
            parent_row = element.find_parent('tr')
            if parent_row:
                row_data = [td.get_text(strip=True) for td in parent_row.find_all('td')]
                contest_name = row_data[1]
                contest_date = row_data[2]
                contest_duration = row_data[4]

                link_element = parent_row.find_all('td')[1].find('a', href=True)
                contest_link = link_element['href'] if link_element else "N/A"

                try:
                    contest_date_parsed = datetime.strptime(contest_date, "%b %d %Y")
                    time_to_start = (contest_date_parsed.date() - datetime.now(timezone.utc).date()).days
                except ValueError as e:
                    print(f"Error parsing date {contest_date}: {e}")
                    continue

                contests.append({
                    'name': contest_name,
                    'date': contest_date_parsed.strftime("%Y-%m-%d"),
                    'duration': contest_duration,
                    'before_start': time_to_start,
                    'link': contest_link
                })

        await browser.close()

    return contests

async def scrape_contests2():
    """Fetch upcoming contests from the second URL."""
    def extract_contest_link(calendar_url):
        parsed_url = urlparse(calendar_url)
        query_params = parse_qs(parsed_url.query)
        contest_link = query_params.get('location', ["N/A"])[0]
        return contest_link

    contests = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://codolio.com/event-tracker")
        await page.wait_for_timeout(5000) 

        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')

        contest_containers = soup.find_all('div', class_='flex flex-col flex-1 min-w-[300px] w-full lg:max-w-[400px] gap-2 p-4 bg-white dark:bg-darkBox-900 dark:border-darkBorder-800 border border-gray-300 rounded-xl')

        for container in contest_containers:
            contest_name_tag = container.find('h3', class_='w-full overflow-hidden whitespace-nowrap text-sm font-[450]')
            contest_name = contest_name_tag.get_text(strip=True) if contest_name_tag else "N/A"

            date_time_tag = container.find('div', class_='inline-flex items-center ml-2 text-sm text-gray-500 dark:text-darkText-400')
            date_time_parts = date_time_tag.find_all('span') if date_time_tag else []
            contest_date = date_time_parts[0].get_text(strip=True) if len(date_time_parts) > 0 else "N/A"
            contest_time = " - ".join(part.get_text(strip=True) for part in date_time_parts[1:]) if len(date_time_parts) > 1 else "N/A"
            stat = "Upcoming"

            link_tag = container.find('a', href=True)
            calendar_link = link_tag['href'] if link_tag else "N/A"
            contest_link = extract_contest_link(calendar_link)

            contests.append({
                'name': contest_name,
                'date': contest_date,
                'time': contest_time,
                'status': stat,
                'link': contest_link
            })
                
        await browser.close()
    
    return contests

@bot.tree.command(name="codeforces")
async def codeforces(interaction: discord.Interaction):
    """Respond with upcoming Codeforces contests."""
    await interaction.response.defer()
    upcoming_contests = await scrape_contests()
    if not upcoming_contests:
        await interaction.followup.send("No upcoming contests found.")
        return

    message = "**Upcoming Codeforces Contests:**\n"
    for contest in upcoming_contests:
        message_part = f"- **[{contest['name']}]({contest['link']})**\n  Date: {contest['date']}\n  Duration: {contest['duration']}\n  Starts in: {contest['before_start']} days\n\n"
        if len(message + message_part) > 2000:
            await interaction.followup.send(message)
            message = ""
        message += message_part

    if message:
        await interaction.followup.send(message)

@bot.tree.command(name="all_contests")
async def all_contests(interaction: discord.Interaction):
    """Respond with all upcoming contests."""
    await interaction.response.defer()  # Defer the response to avoid timeout
    upcoming_contests = await scrape_contests2()
    if not upcoming_contests:
        await interaction.followup.send("No upcoming contests found.")
        return
    
    message = "**Upcoming Contests:**\n"
    for contest in upcoming_contests:
        message_part = f"- **[{contest['name']}]({contest['link']})**\n  Date: {contest['date']}\n  Time: {contest['time']}\n  Status: {contest['status']}\n\n"
        if len(message + message_part) > 2000:
            await interaction.followup.send(message)
            message = ""
        message += message_part

    if message:
        await interaction.followup.send(message)


@tasks.loop(hours=36)
async def check_for_contests():
    """Background task to notify users about contests starting in less than 3 days."""
    upcoming_contests = await scrape_contests()
    if not upcoming_contests:
        return

    for server_id, config in server_config.items():
        channel_id = config.get("channel_id")
        if not channel_id:
            continue
        
        channel = bot.get_channel(channel_id)
        if not channel:
            continue
        
        for contest in upcoming_contests:
            if contest['before_start'] < 3:
                await channel.send(f":rotating_light: **Reminder!** Contest **[{contest['name']}]({contest['link']})** is starting in {contest['before_start']} days!\nDate: {contest['date']} UTC\nDuration: {contest['duration']}")

# Run the bot
bot.run(DISCORD_TOKEN)