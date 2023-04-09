import bot
import config

if __name__ == '__main__':
    config.init()
    print(config.env)
    print(config.runtime)
    config.runtime['bot_name'] = 'test'
    config.get_system_message()
    print(config.runtime['system_message'])
    bot.run_discord_bot()
