# CP_Lord Bot

![License](https://img.shields.io/badge/license-MIT-blue.svg)

CP_Lord is a Discord bot designed to help competitive programmers stay up-to-date with upcoming contests from popular CP websites like Codeforces and more. The bot scrapes websites for contest information and sends reminders to users.

## Features

- Fetches upcoming contests from Codeforces and other popular CP websites.
- Sends reminders for contests starting in less than 3 days.
- Provides information on contest name, date, duration, and more.
- Easy setup and configuration for your Discord server.

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/Samiul191139/CP_Lord.git
    cd CP_Lord
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Set up environment variables:**
    - Create a `.env` file in the root directory and add your Discord bot token.
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    ```

## Usage

1. **Run the bot:**
    ```sh
    python3 bot.py
    ```

2. **Add the bot to your Discord server:**
    - Use the OAuth2 URL to add the bot to your server.

3. **Commands:**
    - `/codeforces` - Fetches upcoming contests from Codeforces.
    - `/all_contests` - Fetches upcoming contests from all supported CP websites.

## Configuration

- The bot saves server-specific configurations in `server_config.json`.
- The bot fetches contest data using Playwright for web scraping.

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Discord.py](https://discordpy.readthedocs.io/en/stable/)
- [Playwright](https://playwright.dev/python/docs/intro)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## Contact

For any inquiries or feedback, please open an issue on GitHub or reach out to me directly at [samikarim191139@gmail.com].

