import bot
import config

if __name__ == '__main__':
    config.init()
    print(f"env: {config.env}")
    print(f"runtime: {config.runtime}")
    bot.run_discord_bot()
