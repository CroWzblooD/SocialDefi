# AI Influencer Agents for Blockchain Communities

## Problem Statement
The rapid expansion of blockchain technologies and decentralized platforms has created a pressing need for real-time, accessible, and engaging community experiences. Users often struggle to keep up with blockchain news, token prices, community updates, and technical insights. This gap can hinder community engagement, reduce participation, and lead to misinformation. Additionally, navigating the fast-paced environment of blockchain communities across platforms like Telegram or X (formerly Twitter) often feels fragmented and overwhelming.

## Objective
Our project aims to enhance the social experience within blockchain communities by developing **AI-powered influencer-like agents**. These agents will provide real-time insights, answer community questions, engage users interactively, and serve as alpha callers for key updates. To prototype and execute this vision, we will build a **Telegram chatbot** with the following features:

- **Quizzes and Interactive Engagements**: A gamified quiz module to educate users about blockchain concepts, updates, and trends.
- **News and Updates**: Real-time notifications for blockchain news and updates tailored to the community's interests.
- **Token Price Tracking**: A feature to display the current price of tokens and provide historical data or trends.
- **Stats and Analytics**: Insights and data visualizations derived from blockchain analytics, offering actionable information to users.
- **Community Notifications**: Alerts and reminders about events, community milestones, or announcements.

## Project Details
**Solution Name**: AI Influencer Agents for Blockchain Communities

### Target Platforms
- **Telegram** (initial phase)
- Future integrations with X, Discord, and other social platforms.

### Features Overview
| Feature                  | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| Quiz Module              | Users can participate in quizzes about blockchain, NFTs, DeFi, etc.        |
| Real-Time Updates        | Fetches blockchain-related news from trusted sources for concise summaries. |
| Token Price Feature      | Users can query current token prices with historical trends.                |
| Stats and Insights       | Interactive charts derived from blockchain analytics for actionable insights.|
| Custom Notifications      | Personalized alerts for token price changes or upcoming events.             |

## Methodology
1. **Technology Stack**:
   - **Programming Language**: Python or JavaScript (Node.js)
   - **Framework**: Telegram Bot API
   - **Data Fetching**: Integration with APIs like CoinGecko, CoinMarketCap.
   - **Machine Learning (Optional)**: For dynamic quiz question generation.
   - **Hosting**: Cloud-based infrastructure (e.g., AWS, Google Cloud).

2. **Development Phases**:
   - Phase 1: Requirements gathering and chatbot architecture design.
   - Phase 2: Implementing core features: quiz module, real-time updates.
   - Phase 3: Integrating additional features like stats and notifications.
   - Phase 4: User testing and feedback collection.
   - Phase 5: Expanding to other platforms based on feedback.

### Data Sources
- Blockchain news aggregators
- Cryptocurrency price APIs
- On-chain data analytics tools

### User Interaction
- Commands to trigger specific actions (e.g., `/price BTC`, `/quiz`).
- Menu-based interaction for less technical users.
- Notifications for passive interaction.

## Scope of the Solution
- **Immediate Impact**:
  - Enhanced community engagement on Telegram through gamification and real-time updates.
  - Improved user understanding of blockchain concepts.

- **Long-Term Goals**:
  - Scaling to multiple platforms for a cohesive community experience.
  - Expanding features to include AI-driven predictive analytics.

## Additional Details
- **User Experience**: The chatbot will prioritize simplicity and interactivity for all users.

### Security
Data privacy will be a key focus to ensure user queries remain secure while integrating with trusted APIs.

### Monetization Opportunities
- Premium subscriptions for advanced analytics.
- Partnerships with blockchain projects for sponsored content.

## Olas Integration
This project utilizes the Olas network as a foundational layer for enhanced performance in decentralized applications. Olas provides a robust framework for building scalable DApps on Ethereum Layer 2 solutions. The integration of Olas is crucial in this project as it allows the bot to leverage its capabilities in processing transactions efficiently while ensuring low latency and high throughput.

### Where Olas is Used:
- **Network Stats Retrieval**: The bot uses Olas to fetch real-time network statistics which inform users about the current state of the Mode Network.
- **Transaction Processing**: By utilizing Olas' infrastructure, the bot can handle transaction requests quickly without overloading the Ethereum mainnet.
- **Enhanced User Engagement**: Olas supports interactive features that allow users to participate in quizzes about blockchain concepts based on real-time data processed through its network.

For more information about Olas, visit their official website at [Olas Network](https://olas.network/) or check their documentation [here](https://docs.olas.network/).

## Mode Network Overview
Mode Network is an innovative Layer 2 solution designed to enhance scalability and efficiency in the Ethereum ecosystem. It aims to address common challenges faced by developers and users in decentralized applications by providing faster transaction speeds and reduced costs. By leveraging advanced technologies such as zk-rollups and state channels, Mode Network ensures that users can interact seamlessly with DApps without experiencing delays or high fees.

### Key Features of Mode Network:
- **Scalability**: Mode Network significantly increases transaction throughput compared to Ethereum Layer 1.
- **Cost Efficiency**: Lower gas fees make it more affordable for users to engage with DApps.
- **Security**: Built on Ethereum's security model while enhancing performance through Layer 2 solutions.

For more details about Mode Network's architecture and benefits, visit [Mode Network Documentation](https://mode.network/docs).

## Code Overview

The core functionality of the bot is encapsulated within the `ModeBot` class. Below are key components of the code:

### Imports

```python
import os
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv
from web3 import Web3
from datetime import datetime, timedelta
```

### Initialization

The bot initializes necessary configurations including environment variables for API keys.

```python
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
w3 = Web3(Web3.HTTPProvider(os.getenv('MODE_RPC_URL')))
```

### Main Bot Class

The `ModeBot` class manages all functionalities including fetching network stats, handling user commands, processing AI analysis requests, managing quizzes, and setting up alerts.

```python
class ModeBot:
    def __init__(self):
        self.news_cache = []
        self.conversation_history = {}
        self.price_alerts = {}
        self.network_stats_cache = {}
        self.cache_timestamp = None
        self.cache_duration = timedelta(minutes=5)
```

### Key Methods

1. **Fetching Network Stats**
   Retrieves current network statistics such as block height and gas price.
   
```python
async def get_network_stats(self):
    current_time = datetime.now()
    if (self.cache_timestamp is None or current_time - self.cache_timestamp > self.cache_duration or not self.network_stats_cache):
        # Fetch stats logic...
```

2. **Handling Commands**
   Responds to user commands like `/start` by displaying options through inline buttons.

```python
async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Network Stats", callback_data='stats'), InlineKeyboardButton("🤖 AI Analysis", callback_data='ai_analysis')],
        # Other buttons...
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome message...", reply_markup=reply_markup)
```

3. **AI Analysis**
   Generates insights based on current network metrics using AI capabilities.

```python
async def handle_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = await self.get_network_stats()
    # Prepare prompt...
```

4. **Quiz Functionality**
   Manages quizzes by generating questions based on network data.

```python
async def quiz_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Generate quiz questions logic...
```

5. **Running the Bot**
   Initializes the bot application and sets up command handlers.

```python
def run(self):
    app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    app.add_handler(CommandHandler('start', self.start_command))
    # Other handlers...
    app.run_polling(allowed_updates=Update.ALL_TYPES)
```

## Environment Setup

To run this project locally:

1. Clone this repository:

    ```bash
    git clone https://github.com/yourusername/your-repo.git
    cd your-repo
    ```

2. Create a `.env` file in the root directory with the following content:

    ```plaintext
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
    GEMINI_API_KEY=your_gemini_api_key_here
    MODE_RPC_URL=https://mainnet.mode.network
    MODE_CONTRACT_ADDRESS=0x70B1053B873028ed1Bd3411A4e0d43ED6E276B78
    ```

3. Install the necessary packages using pip:

    ```bash
    pip install python-telegram-bot==20.7 python-dotenv==1.0.0 web3==6.11.3 google-generativeai==0.3.1 aiohttp==3.9.1
    ```

4. Ensure you have your API keys set up correctly in the `.env` file before running the bot.

5. Start the bot:

    ```bash
    python your_bot_file.py
    ```

## Snapshots

You can upload images related to your project here:
Bot Interface Example

This project bridges the gap between blockchain data and user engagement by leveraging both Mode Network's capabilities and Olas' infrastructure—creating a thriving community through advanced AI-powered influencer agents.

---

This README now includes detailed sections on code overview while maintaining a professional tone throughout the document. It provides clear instructions on setup while emphasizing important integrations with Mode Network and Olas Network effectively.

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/15106762/68c6177b-7462-48e9-9b5f-e9f9c0baf1b9/paste.txt
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/15106762/33f0b953-06af-4baf-a6a2-f5720d70ad0c/paste.txt
