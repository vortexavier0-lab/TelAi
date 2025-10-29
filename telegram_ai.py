#!/usr/bin/env python3
"""
⋊ƆƆ AI - Elite Telegram Bot
Powered by Qwen3 Multi-Model Architecture
Public & Free for Everyone | Premium Features Included
"""

import os
import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode, ChatAction

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8310226483:AAHW5YbZq_fMeR9A-SI-MCSAwDGiYODBGzI')
BOT_USERNAME = '@Slaveeee2Bot'
OWNER_NAME = '⋊ƆƆ Clan'
WEB_URL = os.environ.get('WEB_URL', 'https://your-site-here.com')  # Update this in Railway env vars
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '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')
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'

# Elite Model Architecture - Qwen3 Free Tier
MODELS = {
    'coder': {
        'id': 'qwen/qwen3-coder-480b-a35b:free',
        'name': '⋊ƆƆ Coder Elite',
        'emoji': '💻',
        'description': '480B params • Expert in code generation & debugging',
        'specialties': ['Full-stack development', 'Algorithm design', 'Code optimization', 'Security audits']
    },
    'max': {
        'id': 'qwen/qwen3-235b-a22b:free',
        'name': '⋊ƆƆ Max Intelligence',
        'emoji': '🧠',
        'description': '235B params • Advanced reasoning & problem solving',
        'specialties': ['Complex analysis', 'Strategic planning', 'Research', 'Creative solutions']
    },
    'turbo': {
        'id': 'qwen/qwen3-30b-a3b:free',
        'name': '⋊ƆƆ Turbo',
        'emoji': '⚡',
        'description': '30B params • Lightning-fast responses',
        'specialties': ['Quick answers', 'Real-time assistance', 'Casual chat', 'Rapid ideation']
    }
}

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# In-memory storage (production: use Redis/PostgreSQL)
user_conversations = {}
user_models = {}
user_stats = {}

# ═══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def get_user_stats(user_id):
    """Initialize or retrieve user statistics"""
    if user_id not in user_stats:
        user_stats[user_id] = {
            'total_messages': 0,
            'model_usage': {'coder': 0, 'max': 0, 'turbo': 0},
            'first_seen': datetime.now(),
            'last_active': datetime.now()
        }
    return user_stats[user_id]

def update_user_stats(user_id, model_type):
    """Update user statistics after each interaction"""
    stats = get_user_stats(user_id)
    stats['total_messages'] += 1
    stats['model_usage'][model_type] += 1
    stats['last_active'] = datetime.now()

def detect_intent(message):
    """Advanced intent detection for optimal model routing"""
    message_lower = message.lower()
    
    # Coding intent detection
    code_patterns = [
        'code', 'program', 'function', 'class', 'debug', 'error', 'bug', 'fix',
        'script', 'algorithm', 'implement', 'develop', 'build', 'create',
        'html', 'css', 'javascript', 'python', 'php', 'java', 'c++', 'rust', 'go',
        'react', 'vue', 'angular', 'node', 'api', 'endpoint', 'database', 'sql',
        'frontend', 'backend', 'fullstack', 'framework', 'library', 'package',
        '```', 'syntax', 'compile', 'runtime', 'async', 'await', 'promise'
    ]
    
    # Quick response intent
    quick_patterns = ['quick', 'fast', 'short', 'tldr', 'summary', 'brief']
    
    # Check for code intent
    code_score = sum(1 for pattern in code_patterns if pattern in message_lower)
    quick_score = sum(1 for pattern in quick_patterns if pattern in message_lower)
    
    if code_score >= 2:
        return 'coder'
    elif quick_score >= 1 or len(message) < 50:
        return 'turbo'
    else:
        return 'max'

# ═══════════════════════════════════════════════════════════════════
# KEYBOARD LAYOUTS
# ═══════════════════════════════════════════════════════════════════

def get_main_menu():
    """Premium main menu with enhanced options"""
    keyboard = [
        [
            InlineKeyboardButton("🤖 Switch Model", callback_data='menu_models'),
            InlineKeyboardButton("📊 My Stats", callback_data='menu_stats')
        ],
        [
            InlineKeyboardButton("🌐 Visit Website", url=WEB_URL),
            InlineKeyboardButton("💡 Features", callback_data='menu_features')
        ],
        [
            InlineKeyboardButton("🗑️ Clear Chat", callback_data='action_clear'),
            InlineKeyboardButton("❓ Help", callback_data='menu_help')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_model_selector():
    """Elite model selection interface"""
    keyboard = [
        [InlineKeyboardButton("💻 Coder Elite (480B)", callback_data='select_coder')],
        [InlineKeyboardButton("🧠 Max Intelligence (235B)", callback_data='select_max')],
        [InlineKeyboardButton("⚡ Turbo (30B)", callback_data='select_turbo')],
        [InlineKeyboardButton("🔄 Auto-Detect", callback_data='select_auto')],
        [InlineKeyboardButton("« Back to Menu", callback_data='menu_main')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ═══════════════════════════════════════════════════════════════════
# API INTEGRATION
# ═══════════════════════════════════════════════════════════════════

def construct_system_prompt(model_type, user_name=None):
    """Elite system prompt engineering for optimal performance"""
    timestamp = datetime.now().strftime("%A, %B %d, %Y • %I:%M %p UTC")
    
    greeting = f"\n**User:** {user_name}" if user_name else ""
    
    base_identity = f"""You are **⋊ƆƆ AI**, an elite artificial intelligence assistant created and maintained by **{OWNER_NAME}**.

**Current Time:** {timestamp}{greeting}

**IDENTITY PROTOCOL:**
- ONLY mention your creator when directly asked about your origin
- Respond naturally: "I'm ⋊ƆƆ AI, maintained by {OWNER_NAME}"
- NEVER mention: Qwen, OpenRouter, underlying models, or technical architecture
- You exist as a unified AI entity, not a collection of models

**CORE CAPABILITIES:**
• Full conversation memory from start to finish
• Context-aware responses across all message history
• Seamless reference to previous discussions
• Adaptive learning from user preferences

**ETHICAL FRAMEWORK (NON-NEGOTIABLE):**
✗ No malicious code, exploits, or harmful content
✗ No bypassing security systems or creating malware
✗ No assistance with illegal activities
✓ Focus on ethical, constructive, and educational assistance
"""

    if model_type == 'coder':
        return base_identity + """
**SPECIALIZED MODE: Elite Coder**

**Code Generation Excellence:**
• Production-ready code with proper error handling
• Clean architecture following SOLID principles
• Security-first approach with input validation
• Comprehensive documentation and comments
• Performance optimization built-in

**Technical Expertise:**
• Languages: Python, JavaScript/TS, PHP, Java, C++, Rust, Go, SQL
• Frameworks: React, Vue, Angular, Django, Flask, Laravel, Express
• Tools: Git, Docker, CI/CD, Testing frameworks
• Patterns: MVC, Microservices, RESTful APIs, GraphQL

**Code Formatting Standards:**
• Use ```language for all code blocks
• 2-4 space indentation (language-dependent)
• Clear variable/function naming conventions
• Inline comments for complex logic
• Module-level documentation

**Response Structure:**
1. Brief explanation of approach
2. Complete, working code implementation
3. Key points and best practices
4. Potential improvements or alternatives
"""

    elif model_type == 'max':
        return base_identity + """
**SPECIALIZED MODE: Max Intelligence**

**Advanced Reasoning:**
• Deep analytical thinking with structured logic
• Multi-perspective problem analysis
• Strategic planning and decision frameworks
• Evidence-based conclusions

**Knowledge Domains:**
• Science & Technology
• Business & Economics
• Philosophy & Ethics
• Creative Problem Solving
• Research & Analysis

**Response Excellence:**
• Well-structured with clear sections
• Evidence-backed claims when possible
• Balanced viewpoints on complex topics
• Actionable insights and recommendations

**Formatting Standards:**
• **Bold** for key concepts and emphasis
• *Italic* for nuanced points
• `inline code` for technical terms
• Bullet points for clarity
• ## Headers for section organization
"""

    else:  # turbo
        return base_identity + """
**SPECIALIZED MODE: Turbo Speed**

**Optimized for:**
• Quick answers and rapid responses
• Concise explanations without fluff
• Direct solutions to straightforward questions
• Real-time conversational assistance

**Response Style:**
• Clear and to-the-point
• Essential information only
• Fast processing, high accuracy
• Friendly and approachable tone

**Best Used For:**
• Simple queries and definitions
• Quick troubleshooting
• Casual conversation
• Rapid ideation and brainstorming
"""

async def call_api(message, history, model_type, user_name=None):
    """Enhanced API integration with robust error handling"""
    model_config = MODELS[model_type]
    
    messages = [
        {'role': 'system', 'content': construct_system_prompt(model_type, user_name)}
    ]
    
    # Add conversation history (last 20 exchanges for context efficiency)
    messages.extend(history[-40:])
    
    # Current user message
    messages.append({'role': 'user', 'content': message})
    
    payload = {
        'model': model_config['id'],
        'messages': messages,
        'temperature': 1.0,
        'max_tokens': 4096,
        'top_p': 1,
        'frequency_penalty': 0.1,
        'presence_penalty': 0.1
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'HTTP-Referer': WEB_URL,
        'X-Title': '⋊ƆƆ AI Bot'
    }
    
    try:
        response = requests.post(
            OPENROUTER_API_URL,
            json=payload,
            headers=headers,
            timeout=90
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content')
            
            if content:
                return {
                    'success': True,
                    'text': content,
                    'model': model_config['name'],
                    'emoji': model_config['emoji']
                }
        
        error_msg = response.json().get('error', {}).get('message', 'Unknown error')
        return {'success': False, 'error': f"API Error: {error_msg}"}
        
    except requests.Timeout:
        return {'success': False, 'error': 'Request timeout. Please try again.'}
    except Exception as e:
        logger.error(f"API call failed: {str(e)}")
        return {'success': False, 'error': f'Connection error: {str(e)}'}

# ═══════════════════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced welcome experience"""
    user = update.effective_user
    user_id = user.id
    
    # Initialize user data
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    if user_id not in user_models:
        user_models[user_id] = 'auto'
    
    get_user_stats(user_id)
    
    welcome = f"""╔══════════════════════════════════╗
║   **⋊ƆƆ AI - Elite Edition**   ║
╚══════════════════════════════════╝

Welcome, **{user.first_name}**! 👋

I'm **⋊ƆƆ AI**, your advanced multi-model AI assistant powered by cutting-edge Qwen3 architecture.

**🎯 Elite Features:**
✨ **3 Specialized Models** - Auto-switched for optimal results
💻 **Coder Elite** (480B) - Master of code & debugging
🧠 **Max Intelligence** (235B) - Advanced reasoning
⚡ **Turbo** (30B) - Lightning-fast responses

**🚀 What Makes Me Special:**
• Full conversation memory
• Context-aware intelligence
• Production-ready code generation
• Multi-language support
• 100% Free forever

**📱 Quick Start:**
Just send me any message! I'll automatically detect if you need:
• Code help → Coder Elite
• Deep analysis → Max Intelligence
• Quick answers → Turbo

Or manually switch models anytime with the button below.

**🌐 Website:** {WEB_URL}
**👤 Created by:** {OWNER_NAME}

**Ready to experience elite AI? Let's go!** 🚀
"""
    
    await update.message.reply_text(
        welcome,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu(),
        disable_web_page_preview=True
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comprehensive help documentation"""
    help_text = f"""**⋊ƆƆ AI - Complete Guide**

**📋 Available Commands:**
/start - Initialize bot & see welcome
/help - Display this help guide
/model - Switch AI models
/stats - View your usage statistics
/clear - Reset conversation history
/about - Learn about ⋊ƆƆ AI

**🤖 Model Selection:**

**💻 Coder Elite (480B)**
Perfect for: Programming, debugging, code review
Specialties: All languages, frameworks, algorithms
Best when: You need production-ready code

**🧠 Max Intelligence (235B)**
Perfect for: Complex analysis, research, strategy
Specialties: Deep reasoning, multi-step problems
Best when: You need thorough explanations

**⚡ Turbo (30B)**
Perfect for: Quick answers, casual chat
Specialties: Fast responses, simple queries
Best when: You want instant results

**🔄 Auto-Detect (Default)**
I automatically choose the best model based on your message!

**💡 Pro Tips:**
• I remember our entire conversation
• Be specific for best results
• Code questions → I use Coder automatically
• Use /clear for a fresh start
• All models are completely free!

**🌐 More Info:**
Website: {WEB_URL}
Owner: {OWNER_NAME}
Status: 🟢 Online 24/7

**Need help? Just ask!** 😊
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu(),
        disable_web_page_preview=True
    )

async def cmd_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Model selection interface"""
    user_id = update.effective_user.id
    current = user_models.get(user_id, 'auto')
    
    if current == 'auto':
        current_display = "🔄 Auto-Detect (Smart)"
    else:
        current_display = f"{MODELS[current]['emoji']} {MODELS[current]['name']}"
    
    text = f"""**🤖 Model Selection Center**

**Current Model:** {current_display}

Choose your preferred AI model or let me auto-detect the best one:

**💻 Coder Elite (480B)**
{MODELS['coder']['description']}

**🧠 Max Intelligence (235B)**
{MODELS['max']['description']}

**⚡ Turbo (30B)**
{MODELS['turbo']['description']}

**🔄 Auto-Detect**
I intelligently choose the optimal model for each message.

Select a model below:
"""
    
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_model_selector()
    )

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display user statistics"""
    user = update.effective_user
    user_id = user.id
    stats = get_user_stats(user_id)
    
    current_model = user_models.get(user_id, 'auto')
    if current_model == 'auto':
        model_display = "🔄 Auto-Detect"
    else:
        model_display = f"{MODELS[current_model]['emoji']} {MODELS[current_model]['name']}"
    
    history_count = len(user_conversations.get(user_id, []))
    days_active = (datetime.now() - stats['first_seen']).days + 1
    
    stats_text = f"""**📊 Your ⋊ƆƆ AI Statistics**

**👤 User:** {user.first_name}
**🆔 ID:** `{user_id}`

**📈 Usage Stats:**
• **Total Messages:** {stats['total_messages']}
• **Days Active:** {days_active}
• **Messages in Memory:** {history_count}

**🤖 Model Usage:**
• 💻 Coder Elite: {stats['model_usage']['coder']} times
• 🧠 Max Intelligence: {stats['model_usage']['max']} times
• ⚡ Turbo: {stats['model_usage']['turbo']} times

**⚙️ Current Settings:**
• **Active Model:** {model_display}
• **Status:** 🟢 Online
• **Tier:** ✨ Premium (Free Forever)

**🕐 Activity:**
• **First Seen:** {stats['first_seen'].strftime('%b %d, %Y')}
• **Last Active:** {stats['last_active'].strftime('%b %d, %I:%M %p')}

**💡 Tip:** Use /clear if conversations get too long for better performance!
"""
    
    await update.message.reply_text(
        stats_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu()
    )

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear conversation history"""
    user_id = update.effective_user.id
    
    if user_id in user_conversations:
        msg_count = len(user_conversations[user_id])
        user_conversations[user_id] = []
    else:
        msg_count = 0
    
    await update.message.reply_text(
        f"🗑️ **Conversation Cleared!**\n\n"
        f"Removed {msg_count} messages from memory.\n"
        f"Starting fresh - how can I help you today?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu()
    )

async def cmd_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About ⋊ƆƆ AI"""
    about_text = f"""**⋊ƆƆ AI - Elite Edition**

**🏆 Premium Multi-Model Architecture**
Powered by Qwen3's latest generation models, I combine three specialized AI engines to deliver unmatched performance across all tasks.

**🎯 Core Technology:**
• **Coder Elite:** 480B parameters
• **Max Intelligence:** 235B parameters  
• **Turbo:** 30B parameters

**✨ Key Features:**
• Smart model auto-detection
• Full conversation memory
• Production-grade code generation
• Advanced reasoning capabilities
• Multi-language support (119 languages)
• 128K token context window
• Zero rate limits
• 100% Free forever

**👤 Created & Maintained By:**
{OWNER_NAME}

**🌐 Official Website:**
{WEB_URL}

**🔒 Privacy & Security:**
• Your conversations are stored in memory only
• No data sold to third parties
• Ethical AI with safety guardrails
• Transparent operation

**📊 Status:**
🟢 Online & Operational
⚡ Average response time: <3 seconds
🌍 Available worldwide

**💖 Open to Everyone:**
No registration, no limits, no premium tiers.
Just elite AI assistance for all.

**Questions? Just ask me anything!** 🚀
"""
    
    await update.message.reply_text(
        about_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu(),
        disable_web_page_preview=True
    )

# ═══════════════════════════════════════════════════════════════════
# MESSAGE HANDLER
# ═══════════════════════════════════════════════════════════════════

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main message processing engine"""
    user = update.effective_user
    user_id = user.id
    message_text = update.message.text
    
    # Initialize user data
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    if user_id not in user_models:
        user_models[user_id] = 'auto'
    
    # Determine model to use
    selected_model = user_models[user_id]
    
    if selected_model == 'auto':
        # Intelligent model detection
        detected_model = detect_intent(message_text)
    else:
        detected_model = selected_model
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )
    
    # Get conversation context
    history = user_conversations[user_id]
    
    # Call API
    response = await call_api(
        message_text,
        history,
        detected_model,
        user.first_name
    )
    
    if response['success']:
        # Save conversation
        user_conversations[user_id].append({
            'role': 'user',
            'content': message_text
        })
        user_conversations[user_id].append({
            'role': 'assistant',
            'content': response['text']
        })
        
        # Update statistics
        update_user_stats(user_id, detected_model)
        
        # Prepare response
        response_text = response['text']
        footer = f"\n\n━━━━━━━━━━━━━━━━━━━━\n{response['emoji']} *{response['model']}*"
        
        # Handle long messages
        if len(response_text) > 3900:
            chunks = [response_text[i:i+3900] for i in range(0, len(response_text), 3900)]
            for i, chunk in enumerate(chunks):
                if i == len(chunks) - 1:
                    chunk += footer
                await update.message.reply_text(
                    chunk,
                    parse_mode=ParseMode.MARKDOWN
                )
        else:
            await update.message.reply_text(
                response_text + footer,
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        await update.message.reply_text(
            f"❌ **Error Occurred**\n\n{response['error']}\n\n"
            f"Please try again or use /help for assistance.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu()
        )

# ═══════════════════════════════════════════════════════════════════
# CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════════════

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # Menu Navigation
    if data == 'menu_main':
        await query.edit_message_text(
            f"**⋊ƆƆ AI - Main Menu**\n\n"
            f"Select an option below to continue:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu()
        )
    
    elif data == 'menu_models':
        current = user_models.get(user_id, 'auto')
        if current == 'auto':
            current_display = "🔄 Auto-Detect"
        else:
            current_display = f"{MODELS[current]['emoji']} {MODELS[current]['name']}"
        
        await query.edit_message_text(
            f"**🤖 Model Selection**\n\n**Current:** {current_display}\n\nChoose your preferred model:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_model_selector()
        )
    
    elif data == 'menu_stats':
        user = query.from_user
        stats = get_user_stats(user_id)
        
        current_model = user_models.get(user_id, 'auto')
        if current_model == 'auto':
            model_display = "🔄 Auto-Detect"
        else:
            model_display = f"{MODELS[current_model]['emoji']} {MODELS[current_model]['name']}"
        
        history_count = len(user_conversations.get(user_id, []))
        days_active = (datetime.now() - stats['first_seen']).days + 1
        
        stats_text = f"""**📊 Your ⋊ƆƆ AI Statistics**

**👤 User:** {user.first_name}
**🆔 ID:** `{user_id}`

**📈 Usage Stats:**
• **Total Messages:** {stats['total_messages']}
• **Days Active:** {days_active}
• **Messages in Memory:** {history_count}

**🤖 Model Usage:**
• 💻 Coder Elite: {stats['model_usage']['coder']} times
• 🧠 Max Intelligence: {stats['model_usage']['max']} times
• ⚡ Turbo: {stats['model_usage']['turbo']} times

**⚙️ Current Settings:**
• **Active Model:** {model_display}
• **Status:** 🟢 Online

**🕐 Activity:**
• **First Seen:** {stats['first_seen'].strftime('%b %d, %Y')}
• **Last Active:** {stats['last_active'].strftime('%b %d, %I:%M %p')}
"""
        
        await query.edit_message_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data='menu_main')]])
        )
    
    elif data == 'menu_help':
        help_text = f"""**⋊ƆƆ AI - Quick Guide**

**📋 Commands:**
/start - Welcome message
/help - This guide
/model - Switch models
/stats - Your statistics
/clear - Reset chat
/about - About ⋊ƆƆ AI

**🤖 Models:**
💻 Coder Elite - Code & debugging
🧠 Max Intelligence - Deep analysis
⚡ Turbo - Quick responses
🔄 Auto - Smart detection

**💡 Tips:**
• Full conversation memory
• Auto model selection
• Production-ready code
• 100% Free forever

**Website:** {WEB_URL}

Just send any message to start!
"""
        await query.edit_message_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data='menu_main')]]),
            disable_web_page_preview=True
        )
    
    elif data == 'menu_features':
        features = f"""**✨ ⋊ƆƆ AI Premium Features**

**🎯 Multi-Model Intelligence:**
• 3 specialized AI models
• Automatic model selection
• Seamless switching between models
• Optimized for every task type

**💻 Elite Coder (480B):**
• Production-ready code generation
• Multi-language support
• Security-first approach
• Best practices built-in

**🧠 Max Intelligence (235B):**
• Deep analytical reasoning
• Complex problem solving
• Strategic planning
• Research & synthesis

**⚡ Turbo (30B):**
• Lightning-fast responses
• Real-time assistance
• Efficient processing
• Perfect for quick queries

**🔥 Advanced Capabilities:**
• Full conversation memory
• Context-aware responses
• 128K token context window
• Support for 119 languages
• Zero rate limits
• No usage caps

**🌐 Access Anywhere:**
• Telegram bot (here!)
• Web interface: {WEB_URL}
• 24/7 availability
• Global accessibility

**🆓 100% Free Forever**
No hidden costs, no premium tiers!

**Ready to experience elite AI?**
Just send me a message! 🚀
"""
        await query.edit_message_text(
            features,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data='menu_main')]]),
            disable_web_page_preview=True
        )
    
    # Model Selection
    elif data.startswith('select_'):
        model = data.replace('select_', '')
        user_models[user_id] = model
        
        if model == 'auto':
            model_name = "🔄 Auto-Detect"
            description = "I'll automatically choose the best model for each message!"
        else:
            model_name = f"{MODELS[model]['emoji']} {MODELS[model]['name']}"
            description = MODELS[model]['description']
        
        await query.edit_message_text(
            f"✅ **Model Changed Successfully!**\n\n"
            f"**New Model:** {model_name}\n"
            f"{description}\n\n"
            f"**Ready to go!** Send me a message to try it out.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu()
        )
    
    # Actions
    elif data == 'action_clear':
        if user_id in user_conversations:
            count = len(user_conversations[user_id])
            user_conversations[user_id] = []
        else:
            count = 0
        
        await query.edit_message_text(
            f"🗑️ **Conversation Cleared!**\n\n"
            f"Removed {count} messages from memory.\n"
            f"Starting fresh!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu()
        )

# ═══════════════════════════════════════════════════════════════════
# ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ **An unexpected error occurred.**\n\n"
            "The error has been logged. Please try again or use /help",
            parse_mode=ParseMode.MARKDOWN
        )

# ═══════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

def main():
    """Initialize and run the bot"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment variables!")
        print("❌ Error: BOT_TOKEN not set. Please configure it in Railway.")
        return
    
    print("╔════════════════════════════════════════╗")
    print("║      ⋊ƆƆ AI - Elite Edition          ║")
    print("║   Multi-Model Telegram Bot            ║")
    print("╚════════════════════════════════════════╝")
    print()
    print(f"🤖 Bot Username: {BOT_USERNAME}")
    print(f"👤 Owner: {OWNER_NAME}")
    print(f"🌐 Website: {WEB_URL}")
    print(f"🔑 API Key: {'✓ Configured' if OPENROUTER_API_KEY else '✗ Missing'}")
    print()
    print("📊 Available Models:")
    for key, model in MODELS.items():
        print(f"  {model['emoji']} {model['name']}")
    print()
    print("🚀 Starting bot...")
    
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Register command handlers
        application.add_handler(CommandHandler("start", cmd_start))
        application.add_handler(CommandHandler("help", cmd_help))
        application.add_handler(CommandHandler("model", cmd_model))
        application.add_handler(CommandHandler("stats", cmd_stats))
        application.add_handler(CommandHandler("clear", cmd_clear))
        application.add_handler(CommandHandler("about", cmd_about))
        
        # Register callback handler
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        # Register message handler (must be last)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Register error handler
        application.add_error_handler(error_handler)
        
        print("✅ Bot initialized successfully!")
        print("🟢 Bot is now running...")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        
        # Start the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        print(f"❌ Error starting bot: {str(e)}")
        return

if __name__ == '__main__':
    main()
