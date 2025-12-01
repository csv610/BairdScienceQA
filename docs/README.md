# BairdScienceQA

An interactive science Q&A application with multiple interfaces (Streamlit UI and CLI) that uses advanced LLM models to answer science questions across various topics.

## Features

- **Multiple Interfaces**: Choose between Streamlit web UI or command-line interface
- **Multiple Models**: Support for Gemini 2.5 Flash, GPT-4, Claude via litellm unified API
- **Text-to-Speech**: Convert answers to audio using Google Text-to-Speech
- **Diverse Questions**: Curated science questions covering Biology, Physics, Chemistry, and more
- **Question Management**: Track and manage question progress, reset when needed

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd BairdScienceQA
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API keys for your preferred LLM provider. Example for Gemini:
```bash
export GEMINI_API_KEY="your-api-key"
```

## Usage

### Streamlit Web Interface

Run the interactive web application:
```bash
streamlit run src/app/bairdqa_sl.py
```

Then open your browser to `http://localhost:8501`

Features:
- Select subject and LLM model from sidebar
- Get random questions from selected subject
- Ask LLM for answers
- Convert and play answers as audio
- Track remaining questions

### CLI Tool

Run the command-line interface to process questions:
```bash
python src/app/bairdqa_cli.py
```

Features:
- Interactive menu to select subject
- Process individual subject or all subjects at once
- Save results to JSON files
- Uses Gemini 2.5 Flash via litellm by default

## Project Structure

```
BairdScienceQA/
├── src/
│   ├── bairdqa.py              # Core module (shared utilities)
│   ├── __init__.py
│   └── app/
│       ├── bairdqa_sl.py       # Streamlit web application
│       ├── bairdqa_cli.py      # Command-line interface
│       └── __init__.py
├── data/
│   └── questions.json          # Question database
├── tests/
│   ├── __init__.py
│   └── test_bairdqa_cli.py    # Unit tests
├── docs/
│   ├── README.md               # Main documentation
│   ├── CODE_REVIEW.md          # Code analysis
│   ├── REFACTORING.md          # Refactoring notes
│   └── PROJECT_STRUCTURE.md    # Structure overview
├── requirements.txt            # Python dependencies
├── Makefile                    # Development commands
└── .gitignore                  # Git ignore rules
```

## Available Models

All models are accessed via litellm API:
- **gemini-2.5-flash** (recommended - fast and efficient)
- **gpt-4** (OpenAI)
- **claude-3-sonnet** (Anthropic)
- Other models supported by litellm

Set appropriate API keys as environment variables (GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY)

## File Formats

### questions.json
```json
{
  "Biology": [
    "What if we could live for a million years?",
    "What makes us human?",
    ...
  ],
  "Physics": [...],
  ...
}
```

### Output JSON (CLI)
```json
{
  "question": "...",
  "answer": "..."
}
```

## Development

### Run tests
```bash
make test
# or
pytest tests/
```

### Format code
```bash
make format
# or
black src/ tests/
```

### Install development dependencies
```bash
make install-dev
```

### Clean up generated files
```bash
make clean
```

### Run the application
```bash
# Web UI
make run-streamlit

# CLI
make run-cli
```

## Requirements

- **litellm**: Unified API for LLM models (supports Gemini, OpenAI, Anthropic, etc.)
- **gTTS**: Google Text-to-Speech for audio generation
- **streamlit**: Web framework for UI
- **vlc**: VLC media player for audio playback
- **pytest**: Testing framework

## Notes

- Audio files (*.mp3) are generated but not committed to git
- API keys should be set as environment variables
- The CLI processes questions sequentially and saves results to JSON
- Streamlit app maintains session state for better UX

## License

MIT

## Contributing

Contributions are welcome! Please ensure tests pass and code is formatted before submitting PRs.
