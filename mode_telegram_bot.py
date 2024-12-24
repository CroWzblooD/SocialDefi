import os
import json
import aiohttp
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv
from web3 import Web3
from datetime import datetime
import requests

# Load environment variables
load_dotenv()

# Configure AI and blockchain
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
w3 = Web3(Web3.HTTPProvider(os.getenv('MODE_RPC_URL')))

class ModeCrossmintBot:
    def __init__(self):
        self.crossmint_api_key = os.getenv('CROSSMINT_API_KEY')
        self.crossmint_client_id = os.getenv('CROSSMINT_CLIENT_ID')
        self.user_wallets = {}
        self.conversation_history = {}

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("🔑 Create Wallet", callback_data='create_wallet'),
                InlineKeyboardButton("💰 Check Balance", callback_data='check_balance')
            ],
            [
                InlineKeyboardButton("📊 Mode Stats", callback_data='stats'),
                InlineKeyboardButton("🤖 AI Analysis", callback_data='ai_analysis')
            ],
            [
                InlineKeyboardButton("🎯 Send Tokens", callback_data='send_tokens'),
                InlineKeyboardButton("🎯 Take Quiz", callback_data='quiz')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Welcome to Mode Network AI Wallet Assistant! 🤖\n\n"
            "I can help you with:\n"
            "• Creating and managing your Crossmint wallet 🔑\n"
            "• Sending and receiving tokens 💸\n"
            "• Checking balances and transactions 💰\n"
            "• AI-powered market analysis 📊\n\n"
            "Choose an option to get started!",
            reply_markup=reply_markup
        )

    async def create_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create a new Crossmint wallet"""
        user_id = update.callback_query.from_user.id
        
        try:
            # Call Crossmint API to create wallet
            headers = {
                'x-api-key': self.crossmint_api_key,
                'x-client-id': self.crossmint_client_id,
                'Content-Type': 'application/json'
            }
            
            data = {
                'chain': 'MODE',
                'type': 'evm'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.crossmint.com/api/v1-alpha1/wallets',
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        wallet_data = await response.json()
                        self.user_wallets[user_id] = wallet_data['address']
                        
                        await update.callback_query.message.reply_text(
                            f"✅ Wallet created successfully!\n\n"
                            f"Your Mode Network wallet address:\n`{wallet_data['address']}`\n\n"
                            f"Keep this address safe! You'll need it for transactions.",
                            parse_mode='Markdown'
                        )
                    else:
                        error_data = await response.text()
                        print(f"Wallet creation error: {error_data}")
                        await update.callback_query.message.reply_text(
                            "Sorry, couldn't create wallet. Please try again later."
                        )
                        
        except Exception as e:
            print(f"Error creating wallet: {str(e)}")
            await update.callback_query.message.reply_text(
                "Error creating wallet. Please try again."
            )

    async def check_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if user_id not in self.user_wallets:
            await update.callback_query.message.reply_text(
                "You need to create a wallet first! Click 'Create Wallet'"
            )
            return
            
        try:
            # Get balance from Crossmint
            headers = {
                'x-api-key': self.crossmint_api_key,
                'x-client-id': self.crossmint_client_id
            }
            
            response = requests.get(
                f'https://api.crossmint.com/v1/wallets/{self.user_wallets[user_id]}/balance',
                headers=headers
            )
            
            if response.status_code == 200:
                balance_data = response.json()
                
                await update.callback_query.message.reply_text(
                    f"💰 Wallet Balance:\n\n"
                    f"MODE: {balance_data.get('mode', 0)}\n"
                    f"ETH: {balance_data.get('eth', 0)}\n\n"
                    f"Wallet Address:\n`{self.user_wallets[user_id]}`",
                    parse_mode='Markdown'
                )
            else:
                await update.callback_query.message.reply_text(
                    "Couldn't fetch balance. Please try again later."
                )
                
        except Exception as e:
            await update.callback_query.message.reply_text(
                "Error checking balance. Please try again."
            )

    async def handle_ai_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # Get network stats
            block_number = w3.eth.block_number
            gas_price = w3.eth.gas_price
            
            # Get wallet stats if available
            user_id = update.effective_user.id
            wallet_stats = "No wallet created yet"
            if user_id in self.user_wallets:
                wallet_stats = f"Wallet active: {self.user_wallets[user_id][:8]}..."
            
            prompt = f"""
            Analyze Mode Network status:
            - Block height: {block_number}
            - Gas price: {w3.from_wei(gas_price, 'gwei')} Gwei
            - Wallet status: {wallet_stats}
            
            Provide insights about network performance and recommendations for wallet usage.
            """
            
            response = model.generate_content(prompt)
            
            await update.callback_query.message.reply_text(
                f"�� Mode Network Analysis:\n\n"
                f"Current Stats:\n"
                f"• Block: {block_number:,}\n"
                f"• Gas: {w3.from_wei(gas_price, 'gwei'):.2f} Gwei\n\n"
                f"AI Insights:\n{response.text}"
            )
            
        except Exception as e:
            await update.callback_query.message.reply_text(
                "Sorry, couldn't complete the analysis. Please try again later."
            )

    async def send_tokens(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if user_id not in self.user_wallets:
            await update.callback_query.message.reply_text(
                "You need to create a wallet first! Click 'Create Wallet'"
            )
            return
            
        # Start token sending process
        await update.callback_query.message.reply_text(
            "To send tokens, please provide:\n"
            "1. Recipient address\n"
            "2. Amount\n"
            "3. Token type (MODE/ETH)\n\n"
            "Format: send <address> <amount> <token>"
        )
        
        # Set user state to expect send details
        context.user_data['awaiting_send_details'] = True

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_text = update.message.text.lower()
        user_id = update.effective_user.id
        
        # Handle send token command
        if context.user_data.get('awaiting_send_details') and message_text.startswith('send'):
            try:
                _, recipient, amount, token = message_text.split()
                
                # Call Crossmint API to send tokens
                headers = {
                    'x-api-key': self.crossmint_api_key,
                    'x-client-id': self.crossmint_client_id
                }
                
                data = {
                    'from': self.user_wallets[user_id],
                    'to': recipient,
                    'amount': amount,
                    'token': token.upper()
                }
                
                response = requests.post(
                    'https://api.crossmint.com/v1/transactions',
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    tx_data = response.json()
                    await update.message.reply_text(
                        f"✅ Transaction sent!\n\n"
                        f"Amount: {amount} {token.upper()}\n"
                        f"To: {recipient[:8]}...\n"
                        f"Transaction ID: {tx_data['id']}"
                    )
                else:
                    await update.message.reply_text(
                        "Transaction failed. Please check details and try again."
                    )
                    
                context.user_data['awaiting_send_details'] = False
                
            except Exception as e:
                await update.message.reply_text(
                    "Invalid format. Please use: send <address> <amount> <token>"
                )
                
        else:
            # Handle general questions with AI
            try:
                prompt = f"User question about Mode Network: {message_text}"
                response = model.generate_content(prompt)
                await update.message.reply_text(response.text)
            except Exception as e:
                await update.message.reply_text(
                    "I couldn't process that. Please try again."
                )

    async def quiz_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Mode Network quiz"""
        questions = [
            {
                'question': 'What type of network is Mode?',
                'options': [
                    'Layer 1 Blockchain',
                    'Layer 2 on Ethereum',
                    'Layer 3 Protocol',
                    'Sidechain'
                ],
                'correct': 1
            },
            {
                'question': 'What is the main benefit of Mode Network?',
                'options': [
                    'High gas fees',
                    'Slow transactions',
                    'Ethereum scalability',
                    'No smart contracts'
                ],
                'correct': 2
            },
            {
                'question': 'Which wallet type does Mode support?',
                'options': [
                    'Only hardware wallets',
                    'Only paper wallets',
                    'EVM compatible wallets',
                    'Bitcoin wallets'
                ],
                'correct': 2
            }
        ]
        
        context.user_data['quiz'] = {
            'questions': questions,
            'current': 0,
            'score': 0
        }
        
        await self.send_quiz_question(update, context)

    async def send_quiz_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send quiz question"""
        quiz = context.user_data['quiz']
        current_q = quiz['questions'][quiz['current']]
        
        keyboard = [
            [InlineKeyboardButton(opt, callback_data=f"quiz_{i}")]
            for i, opt in enumerate(current_q['options'])
        ]
        keyboard.append([InlineKeyboardButton("❌ Exit Quiz", callback_data="quiz_exit")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.message.reply_text(
            f"Question {quiz['current'] + 1}/{len(quiz['questions'])}:\n\n"
            f"{current_q['question']}", 
            reply_markup=reply_markup
        )

    async def handle_quiz_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quiz answers"""
        query = update.callback_query
        
        if query.data == "quiz_exit":
            await query.message.reply_text("Quiz ended. Thanks for playing!")
            context.user_data.pop('quiz', None)
            return
            
        quiz = context.user_data.get('quiz')
        if not quiz:
            await query.message.reply_text("No active quiz. Start a new one!")
            return

        answer_index = int(query.data.split('_')[1])
        current_q = quiz['questions'][quiz['current']]
        
        if answer_index == current_q['correct']:
            quiz['score'] += 1
            await query.message.reply_text("✅ Correct!")
        else:
            await query.message.reply_text(
                f"❌ Wrong! The correct answer was: {current_q['options'][current_q['correct']]}"
            )

        quiz['current'] += 1
        if quiz['current'] < len(quiz['questions']):
            await self.send_quiz_question(update, context)
        else:
            await query.message.reply_text(
                f"🎯 Quiz completed!\n"
                f"Your score: {quiz['score']}/{len(quiz['questions'])}\n\n"
                f"Want to try again? Click /start"
            )
            context.user_data.pop('quiz')

    def run(self):
        app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
        
        # Add handlers
        app.add_handler(CommandHandler('start', self.start_command))
        app.add_handler(CallbackQueryHandler(self.create_wallet, pattern='^create_wallet$'))
        app.add_handler(CallbackQueryHandler(self.check_balance, pattern='^check_balance$'))
        app.add_handler(CallbackQueryHandler(self.handle_ai_analysis, pattern='^ai_analysis$'))
        app.add_handler(CallbackQueryHandler(self.send_tokens, pattern='^send_tokens$'))
        app.add_handler(CallbackQueryHandler(self.quiz_handler, pattern='^quiz$'))
        app.add_handler(CallbackQueryHandler(self.handle_quiz_answer, pattern='^quiz_\d+$'))
        app.add_handler(CallbackQueryHandler(self.handle_quiz_answer, pattern='^quiz_exit$'))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print("Mode Network AI Wallet Assistant is starting...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = ModeCrossmintBot()
    bot.run()