import bot
import config

if __name__ == '__main__':
    config.init()
    print(f"env: {config.env}")
    print(f"runtime: {config.runtime}")
    config.runtime['bot_name'] = 'test'
    config.get_system_message()
    print(f"env: {config.env}")
    print(f"runtime: {config.runtime}")
    bot.run_discord_bot()
