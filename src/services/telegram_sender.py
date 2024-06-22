from src.entity.models import History, User, Car, user_car_association
from src.conf.config import config
import logging
import asyncio
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func 
from sqlalchemy.future import select
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Telegram bot token from BotFather
TOKEN = '7487844433:AAFG1-yZSPdPRr3vWB9Leh23IPh_4XRupaY'  # Replace with your bot's token

# Global variable for the chat ID, updated when /start is called
CHAT_ID = None
EMAIL = None

BIND_URL = 'http://127.0.0.1:8000/api/users/bind_chat_id'

# Example function to get the total parking expenses
async def get_parking_expenses(session: AsyncSession):
    try:
        # Async query to join history, cars, and users tables to get parking time for a user based on their email
        result = await session.execute(
            select(func.sum(History.parking_time))
            .join(Car, History.car_id == Car.id)
            .join(user_car_association, user_car_association.car_id == Car.id)
            .join(User, User.id == user_car_association.user_id)
            .filter(User.email == EMAIL)
        )
        # Get scalar result
        total_parking_time = result.scalar()
        # Return the sum of parking times
        return total_parking_time or 0.0  # If no results, return 0.0
    except Exception as e:
        logging.error(f"Error getting parking expenses: {e}")
        return 0.0
    finally:
        session.close()

# Limit after which notification should be sent
EXPENSE_LIMIT = 100.0

async def check_expenses(application):
    if not CHAT_ID:
        logging.warning("CHAT_ID is not set. Cannot check expenses.")
        return

    expenses = get_parking_expenses()
    logging.info(f"Checking expenses: ${expenses:.2f}")
    if expenses > EXPENSE_LIMIT:
        message = f"Warning! Your accumulated parking expenses have exceeded the limit. Current expenses: ${expenses:.2f}"
        await send_telegram_message(application, message)
        

async def send_telegram_message(application, text):
    try:
        await application.bot.send_message(chat_id=CHAT_ID, text=text)
        logging.info(f"Message sent: {text}")
    except Exception as e:
        logging.error(f"Failed to send message: {e}")
        

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = str(update.effective_chat.id)
    logging.info(f"Chat ID set to: {CHAT_ID}")
    
        
        
async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global EMAIL
    EMAIL = update.message.text
    print(EMAIL)
    logging.info(f"Received email: {EMAIL}")

    # Send email and chat_id to the server
    async with aiohttp.ClientSession() as session:
        async with session.post(BIND_URL, json={"email": EMAIL, "chat_id": CHAT_ID}) as response:
            if response.status == 200:
                try:
                    await context.bot.send_message(chat_id=CHAT_ID, text=f"Your chat ID has been successfully bound to your account. Your chat ID is {CHAT_ID}")
                    logging.info("Chat ID bound successfully. Start message sent.")
                except Exception as e:
                    logging.error(f"Failed to send start message: {e}")
            else:
                await context.bot.send_message(chat_id=CHAT_ID, text="There was an error binding your chat ID. Please try again.")
                logging.error("Failed to bind chat ID.")
                

async def periodic_check(application):
    while True:
        try:
            if CHAT_ID:
                await check_expenses(application)
            else:
                logging.warning("Waiting for CHAT_ID to be set before checking expenses.")
            await asyncio.sleep(60)  # Check every 60 seconds
        except Exception as e:
            logging.error(f"Error in periodic_check: {e}")
            break
        
        
async def main():
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TOKEN).build()

    # Register the start command handler
    application.add_handler(CommandHandler("start", start))
    
    # Register the message handler for receiving email
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, email_handler))

    # Start polling and periodic checking
    async with application:
        # Run the periodic check in the background
        asyncio.create_task(periodic_check(application))
        await application.start()
        await application.updater.start_polling()

        # Keep the application running until interrupted
        try:
            while True:
                await asyncio.sleep(1)  # Keep the loop alive
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt received. Shutting down...")
        finally:
            await application.stop()


    """ 
    work for main.py
    
    """
async def run_bot(token: str):
    application = ApplicationBuilder().token(token).build()

    # Register the start command handler
    application.add_handler(CommandHandler("start", start))
    
    # Register the message handler for receiving email
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, email_handler))

    # Start polling and periodic checking
    async with application:
        # Run the periodic check in the background
        asyncio.create_task(periodic_check(application))
        await application.start()
        await application.updater.start_polling()

        # Keep the application running until interrupted
        try:
            while True:
                await asyncio.sleep(3600)  # Sleep for an hour to keep alive
        except asyncio.CancelledError:
            logging.info("Bot interrupted and shutting down.")
        finally:
            await application.stop()



if __name__ == '__main__':
    # Handle running inside an already active event loop
    try:
        if not asyncio.get_event_loop().is_running():
            asyncio.run(main())
        else:
            loop = asyncio.get_event_loop()
            loop.create_task(main())
    except RuntimeError as e:
        if 'This event loop is already running' in str(e):
            loop = asyncio.get_event_loop()
            loop.create_task(main())
        else:
            raise
