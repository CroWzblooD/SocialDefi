import os
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv
from web3 import Web3
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Configure Web3
w3 = Web3(Web3.HTTPProvider(os.getenv('MODE_RPC_URL')))

class ModeBot:
    def __init__(self):
        self.news_cache = []
        self.conversation_history = {}
        self.price_alerts = {}
        self.network_stats_cache = {}
        self.cache_timestamp = None
        self.cache_duration = timedelta(minutes=5)

    async def get_network_stats(self):
        """Get and cache network statistics"""
        current_time = datetime.now()
        
        if (self.cache_timestamp is None or 
            current_time - self.cache_timestamp > self.cache_duration or 
            not self.network_stats_cache):
            
            try:
                latest_block = w3.eth.block_number
                gas_price = w3.eth.gas_price
                
                # Get additional network metrics
                block = w3.eth.get_block(latest_block)
                transactions = len(block['transactions'])
                
                self.network_stats_cache = {
                    'block_height': latest_block,
                    'gas_price': w3.from_wei(gas_price, 'gwei'),
                    'transactions_last_block': transactions,
                    'block_timestamp': block['timestamp'],
                    'block_size': len(w3.to_hex(block['size'])) if 'size' in block else 'N/A'
                }
                self.cache_timestamp = current_time
                
            except Exception as e:
                print(f"Error fetching network stats: {e}")
                return None
                
        return self.network_stats_cache

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("📊 Network Stats", callback_data='stats'),
                InlineKeyboardButton("🤖 AI Analysis", callback_data='ai_analysis')
            ],
            [
                InlineKeyboardButton("🎯 Mode Quiz", callback_data='quiz'),
                InlineKeyboardButton("📰 Latest News", callback_data='news')
            ],
            [
                InlineKeyboardButton("⚡ Price Alerts", callback_data='price_alerts'),
                InlineKeyboardButton("📈 Network Metrics", callback_data='metrics')
            ],
            [
                InlineKeyboardButton("❓ Help", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Welcome to Mode Network Assistant! 🤖\n\n"
            "I combine AI analysis and real-time blockchain data to help you with:\n"
            "• Live Mode Network statistics 📊\n"
            "• AI-powered insights 🤖\n"
            "• Custom price alerts ⚡\n"
            "• Network performance metrics 📈\n"
            "• Latest updates and news 📰\n\n"
            "Choose an option or ask me anything about Mode Network!",
            reply_markup=reply_markup
        )

    async def handle_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle AI analysis using network data and Gemini"""
        try:
            # Get network stats
            stats = await self.get_network_stats()
            if not stats:
                await update.callback_query.message.reply_text(
                    "Unable to fetch network stats. Please try again later."
                )
                return

            # Prepare analysis prompt
            prompt = f"""
            Analyze Mode Network based on these metrics:
            - Latest block: {stats['block_height']:,}
            - Gas price: {stats['gas_price']} Gwei
            - Transactions in last block: {stats['transactions_last_block']}
            - Block size: {stats['block_size']}
            
            Provide comprehensive insights about:
            1. Network performance and health
            2. Transaction activity and trends
            3. Gas price analysis
            4. Recommendations for network usage
            """
            
            ai_response = model.generate_content(prompt)
            
            # Format and send response
            response_text = (
                f"🔍 Mode Network Analysis\n\n"
                f"📊 Current Metrics:\n"
                f"• Block Height: {stats['block_height']:,}\n"
                f"• Gas Price: {stats['gas_price']} Gwei\n"
                f"• Transactions (Last Block): {stats['transactions_last_block']}\n"
                f"• Block Size: {stats['block_size']}\n\n"
                f"🤖 AI Insights:\n{ai_response.text}"
            )
            
            await update.callback_query.message.reply_text(response_text)
            
        except Exception as e:
            await update.callback_query.message.reply_text(
                "Sorry, couldn't complete the analysis. Please try again later."
            )

    async def handle_price_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle price alert settings"""
        user_id = update.effective_user.id
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Set Alert", callback_data='set_alert'),
                InlineKeyboardButton("📝 View Alerts", callback_data='view_alerts')
            ],
            [
                InlineKeyboardButton("🗑️ Clear Alerts", callback_data='clear_alerts')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.message.reply_text(
            "📈 Price Alert Settings\n\n"
            "• Set custom price alerts\n"
            "• View your active alerts\n"
            "• Clear all alerts\n\n"
            "What would you like to do?",
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        message_text = update.message.text

        # Get network context
        stats = await self.get_network_stats()
        if not stats:
            stats = {"status": "unavailable"}

        # Prepare AI prompt with context
        prompt = f"""
        Context:
        - Mode Network Block Height: {stats.get('block_height', 'N/A')}
        - Current Gas Price: {stats.get('gas_price', 'N/A')} Gwei
        - Recent Transactions: {stats.get('transactions_last_block', 'N/A')}
        
        User Question: {message_text}
        
        Provide a helpful and informative response about Mode Network.
        Focus on accuracy and practical insights.
        """

        try:
            response = model.generate_content(prompt)
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text(
                "I encountered an error processing your question. Please try asking in a different way."
            )

    async def quiz_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate dynamic quiz questions using network data"""
        try:
            stats = await self.get_network_stats()
            
            questions = [
                {
                    'question': 'What is Mode Network?',
                    'options': [
                        'Layer 1 Blockchain',
                        'Layer 2 on Ethereum',
                        'DeFi Protocol',
                        'NFT Platform'
                    ],
                    'correct': 1,
                    'explanation': 'Mode is an Ethereum Layer 2 scaling solution that enhances transaction speed and reduces costs.'
                },
                {
                    'question': f'What is the approximate current block height of Mode Network?',
                    'options': [
                        f'{stats["block_height"]-1000:,}',
                        f'{stats["block_height"]:,}',
                        f'{stats["block_height"]+1000:,}',
                        'None of the above'
                    ],
                    'correct': 1,
                    'explanation': f'The current block height is {stats["block_height"]:,}.'
                },
                {
                    'question': 'What is the typical gas price range on Mode Network?',
                    'options': [
                        'Similar to Ethereum L1',
                        'Much higher than L1',
                        'Much lower than L1',
                        'Zero gas fees'
                    ],
                    'correct': 2,
                    'explanation': 'Mode Network typically has much lower gas fees compared to Ethereum L1.'
                }
            ]
            
            context.user_data['quiz'] = {
                'questions': questions,
                'current': 0,
                'score': 0
            }
            
            await self.send_quiz_question(update, context)
        except Exception as e:
            await update.callback_query.message.reply_text(
                "Sorry, couldn't start the quiz. Please try again later."
            )

    async def send_quiz_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        quiz = context.user_data['quiz']
        current_q = quiz['questions'][quiz['current']]
        
        keyboard = [
            [InlineKeyboardButton(opt, callback_data=f"quiz_{i}")]
            for i, opt in enumerate(current_q['options'])
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        question_text = (
            f"Question {quiz['current'] + 1} of {len(quiz['questions'])}:\n\n"
            f"{current_q['question']}"
        )
        
        await update.callback_query.message.reply_text(
            question_text,
            reply_markup=reply_markup
        )

    def run(self):
        app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
        
        # Add handlers
        app.add_handler(CommandHandler('start', self.start_command))
        app.add_handler(CallbackQueryHandler(self.handle_ai_analysis, pattern='^ai_analysis$'))
        app.add_handler(CallbackQueryHandler(self.quiz_handler, pattern='^quiz$'))
        app.add_handler(CallbackQueryHandler(self.handle_price_alerts, pattern='^price_alerts$'))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print("Mode Bot is starting with enhanced features...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = ModeBot()
    bot.run()