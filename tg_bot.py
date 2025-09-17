# Oeba720 BYPASS MAKER-----------------------@Oeba720

import logging
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# States for conversation
START, CHOOSING_OPTION, ENTER_OFFSETS = range(3)

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

def generate_patch_lib(offsets):
    """
    Generates PATCH_LIB lines for the given offsets.

    Args:
        offsets (list): List of offset strings, e.g., ["0x12345678", "0x87654321"]

    Returns:
        str: Formatted string of PATCH_LIB lines
    """
    lib_name = "libanogs.so"
    hex_string = "00 00 80 D2 C0 03 5F D6"
    patches = []
    for offset in offsets:
        patch = f'PATCH_LIB("{lib_name}", "{offset}", "{hex_string}");'
        patches.append(patch)
    return '\n'.join(patches)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Oeba7 BYPASS MAKER-----------------------@Oeba720\n\n"
        "Choose an option:\n"
        "1. PATCH_LIB\n"
        "2. HOOK_LIB (coming soon)\n"
        "3. Generate CPP file\n\n"
        "Reply with 1, 2, or 3."
    )
    return CHOOSING_OPTION

async def choose_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the user's choice."""
    text = update.message.text.strip()
    if text.lower() == "done":
        await update.message.reply_text("Conversation cancelled.")
        return ConversationHandler.END
    if text == "1":
        context.user_data['mode'] = 'text'
        await update.message.reply_text("Enter offsets (single or multiple, newline separated, e.g.:\n0x12345678\nsub_505AC0):")
        return ENTER_OFFSETS
    elif text == "2":
        await update.message.reply_text("HOOK_LIB feature not implemented yet.")
        return START
    elif text == "3":
        context.user_data['mode'] = 'cpp'
        await update.message.reply_text("Enter offsets (single or multiple, newline separated, e.g.:\n0x12345678\n0x87654321):")
        return ENTER_OFFSETS
    else:
        await update.message.reply_text("Invalid choice. Reply with 1, 2, or 3.")
        return CHOOSING_OPTION

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
    patches = generate_patch_lib(offsets)
    mode = context.user_data.get('mode', 'text')
    if mode == 'cpp':
        # Create CPP content
        cpp_content = f"// Oeba720 BYPASS MAKER-----------------------@Oeba720\n\n// {converted_msg}\n\n{patches}\n"
        # Send as document
        import io
        bio = io.BytesIO(cpp_content.encode('utf-8'))
        bio.name = 'generated_patches.cpp'
        await update.message.reply_document(bio, caption="Generated CPP file with PATCH_LIB lines.")
    else:
        await update.message.reply_text(f"Generated PATCH_LIB lines:\n{patches}")
    await update.message.reply_text("Choose again: 1. PATCH_LIB 2. HOOK_LIB 3. Generate CPP file\nType 'done' to cancel conversation.")
    return CHOOSING_OPTION

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Oeba720 BYPASS MAKER-----------------------@Oeba720\n\n"
        "Available commands:\n"
        "/start - Start the bot and choose options\n"
        "/help - Show this help message\n"
        "/owner - Show owner information\n"
        "/cancel - Cancel the current conversation\n\n"
        "How to use:\n"
        "1. Use /start to begin.\n"
        "2. Choose 1 for PATCH_LIB (text output), 3 for Generate CPP file.\n"
        "3. Enter offsets or sub_ (e.g., sub_505AC0), one per line.\n"
        "4. Receive generated PATCH_LIB lines or CPP file.\n"
        "5. Repeat or choose again."
    )

async def owner_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send owner information."""
    await update.message.reply_text("@Oeba720")

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

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_option)],
            ENTER_OFFSETS: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_offsets)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
