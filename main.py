import bot
import config

if __name__ == '__main__':
    config.init()
    print(config.env)
    print(config.runtime)
    bot.run_discord_bot()
