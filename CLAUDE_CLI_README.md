# Claude CLI Tools

This project includes several ways to integrate Claude AI with your terminal for enhanced productivity and travel planning assistance.

## 🚀 Quick Start

### 1. Set up your API key

Add your Anthropic API key to your `.env` file:

```bash
# Add this line to your .env file
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 2. Get your Anthropic API key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Create a new API key
4. Copy the key and add it to your `.env` file

## 📦 Available Tools

### 1. General Claude CLI (`claude_cli.py`)

A general-purpose Claude interface for any type of conversation.

**Usage:**
```bash
# Interactive mode
python claude_cli.py

# Single message
python claude_cli.py "What's the weather like in Tokyo?"

# Using the wrapper script
./claude "Help me write a Python function"
```

**Features:**
- Interactive chat mode
- Single message mode
- Coding mode (`code` command)
- Normal mode (`normal` command)
- Clear screen (`clear` command)

### 2. Travel Assistant CLI (`claude_travel_assistant.py`)

Specialized Claude interface for travel planning that integrates with your travel booking system.

**Usage:**
```bash
# Interactive mode
python claude_travel_assistant.py

# Single travel question
python claude_travel_assistant.py "What are the best places to visit in Paris?"
```

**Features:**
- Travel-specific system prompt
- Backend status checking (`status` command)
- Backend startup (`start` command)
- Integration with travel booking API

### 3. Shell Wrapper (`claude`)

Simple shell script wrapper for easy access.

**Usage:**
```bash
# Interactive mode
./claude

# Single message
./claude "Explain Docker containers"
```

## 🛠️ Installation

### Prerequisites

Make sure you have the required Python packages:

```bash
pip install requests python-dotenv
```

### Make scripts executable

```bash
chmod +x claude_cli.py
chmod +x claude_travel_assistant.py
chmod +x claude
```

## 📋 Commands Reference

### General CLI Commands
- `help` - Show available commands
- `quit` / `exit` / `q` - Exit the program
- `clear` - Clear the screen
- `code` - Switch to coding mode
- `normal` - Switch to normal mode

### Travel Assistant Commands
- `help` - Show available commands
- `quit` / `exit` / `q` - Exit the program
- `status` - Check if backend is running
- `start` - Start the travel planning backend
- `clear` - Clear the screen

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional (for travel assistant)
OPENAI_API_KEY=your_openai_api_key_here
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret
```

### Model Configuration

You can modify the Claude model used by editing the `model` variable in the Python files:

```python
# Available models:
# claude-3-5-sonnet-20241022 (default)
# claude-3-opus-20240229
# claude-3-sonnet-20240229
# claude-3-haiku-20240307
```

## 💡 Usage Examples

### General Assistance
```bash
# Ask for help with coding
./claude "Write a Python function to sort a list"

# Get explanations
./claude "Explain how Docker containers work"

# Interactive mode for extended conversations
./claude
```

### Travel Planning
```bash
# Get travel recommendations
python claude_travel_assistant.py "What should I do in Tokyo for 3 days?"

# Check weather
python claude_travel_assistant.py "What's the weather like in London?"

# Interactive travel planning
python claude_travel_assistant.py
```

## 🔗 Integration with Travel System

The travel assistant integrates with your existing travel booking system:

- **Backend Status**: Check if the travel planning backend is running
- **API Integration**: Suggests using the booking system API endpoints
- **Travel Knowledge**: Provides travel-specific assistance

### Available API Endpoints
- `POST /generate_plan` - Generate AI travel plan
- `POST /confirm_plan` - Confirm and book plan
- `GET /get_user_plans/{wallet}` - Get user plans

## 🐛 Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   ❌ Error: ANTHROPIC_API_KEY not found in environment variables
   ```
   **Solution**: Add your API key to the `.env` file

2. **Module Not Found**
   ```
   ModuleNotFoundError: No module named 'requests'
   ```
   **Solution**: Install required packages:
   ```bash
   pip install requests python-dotenv
   ```

3. **Permission Denied**
   ```
   Permission denied: ./claude
   ```
   **Solution**: Make scripts executable:
   ```bash
   chmod +x claude claude_cli.py claude_travel_assistant.py
   ```

### Backend Integration Issues

1. **Backend Not Running**
   ```
   ❌ Backend is not running
   ```
   **Solution**: Use the `start` command or run:
   ```bash
   ./start_backend.sh
   ```

2. **Connection Refused**
   ```
   ❌ Error: Connection refused
   ```
   **Solution**: Ensure the backend is running on port 8000

## 🔒 Security Notes

- Never commit your API keys to version control
- Use environment variables for sensitive data
- The `.env` file is already in `.gitignore`
- API keys are only used for local development

## 📚 Advanced Usage

### Custom System Prompts

You can modify the system prompts in the Python files to customize Claude's behavior:

```python
def get_system_prompt(self) -> str:
    return """Your custom system prompt here..."""
```

### Integration with Other Tools

The CLI tools can be integrated with other shell scripts:

```bash
#!/bin/bash
# Example: Use Claude to generate code comments
response=$(./claude "Add comments to this Python function: $1")
echo "$response" > commented_function.py
```

## 🤝 Contributing

To add new features to the Claude CLI tools:

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the x402 Travel Planning System and follows the same license terms. 