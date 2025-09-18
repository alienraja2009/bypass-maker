# bypass maker bot

import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# States for conversation
START, CHOOSING_OPTION, CHOOSING_LIB, CHOOSING_HEX, ENTER_OFFSETS, REPORT_COLLECT = range(6)

# Bot mode and owner
MODE = 'public'
OWNER_ID = 6198639708
REPORT_COUNT = 0

# Stats
TOTAL_USERS = set()
ACTIVE_USERS = set()
MONTHLY_USERS = set()
BLOCKED_USERS = set()
REPORTING_USERS = set()

def check_access(update: Update) -> bool:
    """Check if user has access based on mode."""
    if MODE == 'private' and update.effective_user.id != OWNER_ID:
        return False
    return True

async def public_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set bot to public mode."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can change the bot mode.")
        return
    global MODE
    MODE = 'public'
    await update.message.reply_text("Bot is now in public mode. Anyone can use it.")

async def private_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set bot to private mode."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can change the bot mode.")
        return
    global MODE
    MODE = 'private'
    await update.message.reply_text("Bot is now in private mode. Only the owner can use it.")

async def choose_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the user's choice."""
    if not check_access(update):
        await update.message.reply_text("Bot is in private mode. Access denied.")
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "1":
        context.user_data['patch_type'] = 'PATCH_LIB'
        context.user_data['mode'] = 'text'
        await update.message.reply_text(
            "Choose the Lib:\n"
            "1. libanogs.so\n"
            "2. libanort.so\n"
            "3. libUE4.so\n"
            "4. libhdmpve.so\n"
            "5. libTBlueData.so\n"
            "6. libAntsVoice.so\n"
            "7. libRoosterNN.so\n\n"
            "Reply with 1-7 or /cancel to cancel."
        )
        return CHOOSING_LIB
    elif text == "2":
        context.user_data['patch_type'] = 'MemoryPatch'
        context.user_data['mode'] = 'text'
        await update.message.reply_text(
            "Choose the Lib:\n"
            "1. libanogs.so\n"
            "2. libanort.so\n"
            "3. libUE4.so\n"
            "4. libhdmpve.so\n"
            "5. libTBlueData.so\n"
            "6. libAntsVoice.so\n"
            "7. libRoosterNN.so\n\n"
            "Reply with 1-7 or /cancel to cancel."
        )
        return CHOOSING_LIB
    elif text == "3":
        await update.message.reply_text("Tools WriteAddr feature coming soon.")
        return CHOOSING_OPTION
    else:
        await update.message.reply_text("Invalid choice. Reply with 1-3.")
        return CHOOSING_OPTION

def convert_sub_to_offset(subs):
    """
    Converts list of sub_ strings to 0x offsets.
    E.g. sub_505AC0 -> 0x505AC0

    Args:
        subs (list): List of strings starting with 'sub_'

    Returns:
        list: List of converted offset strings starting with '0x'
    """
    offsets = []
    for sub in subs:
        if sub.startswith("sub_"):
            offsets.append("0x" + sub[4:])
        else:
            offsets.append(sub)
    return offsets

def generate_patch_lib(offsets, context):
    """
    Generates PATCH_LIB or MemoryPatch or WriteAddr lines for the given offsets.

    Args:
        offsets (list): List of offset strings, e.g., ["0x12345678", "0x87654321"]
        context: Telegram context

    Returns:
        str: Formatted string of patch lines
    """
    lib_name = context.user_data.get('lib_name', "libanogs.so")
    hex_value = context.user_data.get('hex_value', "00 00 80 D2 C0 03 5F D6")
    patch_type = context.user_data.get('patch_type', 'PATCH_LIB')
    patches = []
    for offset in offsets:
        if patch_type == 'PATCH_LIB':
            patch = f'PATCH_LIB("{lib_name}", "{offset}", "{hex_value}");'
        elif patch_type == 'MemoryPatch':
            # Remove 0x prefix for MemoryPatch
            clean_offset = offset.replace("0x", "")
            patch = f'MemoryPatch::createWithHex("{lib_name}", 0x{clean_offset}, "{hex_value}").Modify();'
        elif patch_type == 'WriteAddr':
            # Remove 0x prefix for WriteAddr
            clean_offset = offset.replace("0x", "")
            patch = f'Tools::WriteAddr("{lib_name}", 0x{clean_offset}, "{hex_value}");'
        else:
            patch = f'// Unknown patch type for offset {offset}'
        patches.append(patch)
    return '\n'.join(patches)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    global OWNER_ID
    if OWNER_ID is None:
        OWNER_ID = update.effective_user.id
    if not check_access(update):
        await update.message.reply_text("Bot is in private mode. Access denied.")
        return ConversationHandler.END
    await update.message.reply_text(
        "bypass maker bot\n\n"
        "Choose an option:\n"
        "1. PATCH_LIB\n"
        "2. MemoryPatch\n"
        "3. Tools WriteAddr\n\n"
        "Reply with 1-3 or /cancel to cancel."
    )
    return CHOOSING_OPTION



async def choose_lib(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the lib choice."""
    if not check_access(update):
        await update.message.reply_text("Bot is in private mode. Access denied.")
        return ConversationHandler.END
    text = update.message.text.strip()
    libs = {
        "1": "libanogs.so",
        "2": "libanort.so",
        "3": "libUE4.so",
        "4": "libhdmpve.so",
        "5": "libTBlueData.so",
        "6": "libAntsVoice.so",
        "7": "libRoosterNN.so"
    }
    if text in libs:
        context.user_data['lib_name'] = libs[text]
        await update.message.reply_text(
            "Choose the hex value:\n"
            "1. Best Hex (coming soon)\n"
            "2. Default Hex\n"
            "3. Automatically Matched Hex\n\n"
            "Reply with 1-3 or /cancel to cancel."
        )
        return CHOOSING_HEX
    else:
        await update.message.reply_text("Invalid choice. Reply with 1-7.")
        return CHOOSING_LIB

async def choose_hex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the hex choice."""
    if not check_access(update):
        await update.message.reply_text("Bot is in private mode. Access denied.")
        return ConversationHandler.END
    text = update.message.text.strip()
    if text == "1":
        await update.message.reply_text("Best Hex feature not implemented yet.")
        return CHOOSING_HEX
    hex_options = {
        "2": "00 00 00 00",  # Default Hex
        "3": "00 00 80 D2 C0 03 5F D6"   # Automatically Matched Hex
    }
    if text in hex_options:
        context.user_data['hex_value'] = hex_options[text]
        await update.message.reply_text("Enter offsets (single or multiple, newline separated, e.g.:\n0x12345678\nsub_505AC0):\n\nOr /cancel to cancel.")
        return ENTER_OFFSETS
    else:
        await update.message.reply_text("Invalid choice. Reply with 1-3.")
        return CHOOSING_HEX

async def enter_offsets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the offsets input."""
    offsets_str = update.message.text.strip()
    offsets = [offset.strip() for offset in offsets_str.split('\n') if offset.strip()]
    if not offsets:
        await update.message.reply_text("No offsets provided. Try again.")
        return ENTER_OFFSETS
    # Validate offsets
    for offset in offsets:
        if not (re.match(r'^0x[0-9a-fA-F]+$', offset) or re.match(r'^sub_[0-9a-fA-F]+$', offset)):
            await update.message.reply_text("Invalid offset format. Use 0x followed by hex digits or sub_ followed by hex digits. Try again.")
            return ENTER_OFFSETS
    # Convert sub_ to 0x if needed
    offsets = convert_sub_to_offset(offsets)
    converted_msg = f"Converted offsets: {', '.join(offsets)}"
    await update.message.reply_text(converted_msg)
    patches = generate_patch_lib(offsets, context)
    patch_type = context.user_data.get('patch_type', 'PATCH_LIB')
    await update.message.reply_text(f"Generated {patch_type} lines:\n<pre>{patches}</pre>", parse_mode='HTML')
    await update.message.reply_text("Choose again: 1. PATCH_LIB 2. MemoryPatch 3. Tools WriteAddr\n\nOr /cancel to cancel.")
    return CHOOSING_OPTION

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "bypass maker bot\n\n"
        "Available commands:\n"
        "/start - Start the bot and choose options\n"
        "/help - Show this help message\n"
        "/owner - Show owner information\n"
        "/report - Report an issue or complaint\n"
        "/public - Set bot to public mode (owner only)\n"
        "/private - Set bot to private mode (owner only)\n\n"
        "How to use:\n"
        "1. Use /start to begin.\n"
        "2. Choose 1 for PATCH_LIB, 2 for MemoryPatch, 3 for Tools WriteAddr.\n"
        "3. Choose the lib from the list.\n"
        "4. Choose the hex value from the options.\n"
        "5. Enter offsets or sub_ (e.g., sub_505AC0), one per line.\n"
        "6. Receive generated lines.\n"
        "7. Repeat or choose again.\n\n"
        "For support, contact the owner @Oeba720."
    )

async def owner_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send owner information."""
    await update.message.reply_text("@Oeba720")



async def report_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the report conversation."""
    await update.message.reply_text("Please describe the issue or complaint:")
    return REPORT_COLLECT

async def report_collect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect and send the report."""
    report_text = update.message.text
    global OWNER_ID
    if OWNER_ID:
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"Report from @{update.effective_user.username or update.effective_user.first_name} (ID: {update.effective_user.id}):\n{report_text}"
            )
            global REPORT_COUNT
            REPORT_COUNT += 1
            await update.message.reply_text("Thank you for your report. It has been sent to the owner @Oeba720.")
        except Exception as e:
            await update.message.reply_text("Failed to send report. Please try again later.")
            logger.error(f"Failed to send report: {e}")
    else:
        await update.message.reply_text("Owner not set. Report could not be sent.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text("Conversation cancelled.")
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    application = Application.builder().token("7993301231:AAEq0dIabX5wBDc-nKmNrdGMMOLf__2l50o").build()

    # Add command handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("owner", owner_command))
    application.add_handler(CommandHandler("public", public_command))
    application.add_handler(CommandHandler("private", private_command))

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_option)],
            CHOOSING_LIB: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_lib)],
            CHOOSING_HEX: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_hex)],
            ENTER_OFFSETS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_offsets)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=300,
    )
    application.add_handler(conv_handler)

    # Add report conversation handler
    report_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("report", report_start)],
        states={
            REPORT_COLLECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_collect)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=300,
    )
    application.add_handler(report_conv_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
