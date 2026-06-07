# Project Structure Overview

## Directory Organization

```
BairdScienceQA/
├── baird/                      # Core modules
│   ├── __init__.py            # Package initialization
│   ├── bairdqa.py             # Core module (utilities)
│   └── llm.py                 # LLM functions (ask_llm)
│
├── app/                        # Applications (CLI & Web)
│   ├── __init__.py
│   ├── bairdqa_cli.py         # Command-line interface
│   └── bairdqa_sl.py          # Streamlit web interface
│
├── data/                       # Data files
│   └── questions.json         # Question database
│
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_bairdqa_cli.py   # Unit tests for CLI
│
├── docs/                       # Documentation
│   ├── README.md              # Main documentation
│   ├── CODE_REVIEW.md         # Code analysis report
│   ├── REFACTORING.md         # Refactoring notes
│   └── PROJECT_STRUCTURE.md   # This file
│
├── requirements.txt            # Python dependencies
├── Makefile                    # Development commands
└── .gitignore                  # Git ignore rules
```

## Module Descriptions

### baird/bairdqa.py (Core Module)
**Purpose**: Shared utilities for questions and results

**Functions**:
- `load_questions(file_path)` - Load questions from JSON
- `save_results(data, file_path)` - Save results to JSON
- `process_subject(questions_data, subject)` - Generator for batch processing

### baird/llm.py (LLM Module)
**Purpose**: All LLM-related functions

**Functions**:
- `ask_llm(question, model)` - Ask LLM a question via litellm (single entry point)

**Key Feature**: Single source of truth for all LLM interactions using litellm only

### app/bairdqa_cli.py (CLI Interface)
**Purpose**: Command-line tool for batch processing questions

**Key Functions**:
- `process_and_display()` - Process and display questions
- `main()` - Main CLI entry point with subject selection

**Usage**:
```bash
python app/bairdqa_cli.py
```

### app/bairdqa_sl.py (Web UI)
**Purpose**: Streamlit-based interactive web interface

**Key Functions**:
- `load_questions()` - Cached question loader
- `initialize_session_state()` - Track session state
- `generate_new_question()` - Random question generator
- `text_to_speech()` - Convert answers to audio
- `main()` - Streamlit UI entry point

**Usage**:
```bash
streamlit run app/bairdqa_sl.py
```

## Data Files

### data/questions.json
**Format**:
```json
{
  "Subject": [
    "Question 1",
    "Question 2",
    ...
  ]
}
```

**Contents**: Science questions organized by subject (Biology, Physics, Chemistry, etc.)

## Test Suite

### tests/test_bairdqa_cli.py
**Coverage**:
- Question loading from JSON
- File not found error handling
- Question count validation
- Question content validation

**Run tests**:
```bash
pytest tests/
# or
make test
```

## Development Workflow

### Setup
```bash
pip install -r requirements.txt
```

### Run Application
```bash
# Web UI
make run-streamlit
# or
streamlit run app/bairdqa_sl.py

# CLI
make run-cli
# or
python app/bairdqa_cli.py
```

### Development Tasks
```bash
make install-dev    # Install dev dependencies
make format         # Format code with black
make lint          # Run code linting
make test          # Run tests
make clean         # Clean generated files
```

## Import Paths

### From CLI/Web Interface
```python
from baird.bairdqa import load_questions, save_results, save_results_markdown
from baird.llm import ask_llm
```

### From Tests
```python
sys.path.insert(0, str(Path(__file__).parent.parent / 'baird'))
from bairdqa import load_questions
```

## Key Design Principles

1. **Single Responsibility**: Each module has a clear purpose
2. **DRY (Don't Repeat Yourself)**: Shared code in bairdqa.py
3. **Unified LLM**: All LLM calls through litellm only
4. **Testability**: Core logic separated from UI
5. **Scalability**: Easy to add new interfaces

## File Access Paths

All applications reference files relative to their location:

| File | CLI Path | Web Path |
|------|----------|----------|
| questions.json | `data/questions.json` (via `Path(__file__)`) | `data/questions.json` (via `Path(__file__)`) |
| Output files | `current_dir/*.md` | `current_dir/*.mp3` |

## Architecture Diagram

```
┌─────────────────────────┐
│   baird/bairdqa.py      │
│  • load_questions()      │
│  • save_results()        │
│  • save_results_markdown │
│  • parse_markdown_results│
└────────┬────────────────┘
         │
    ┌────▼──────────┐
    │  baird/llm.py │
    │  • ask_llm()  │  ← Single LLM Entry Point
    └────┬──────────┘
         │
     ┌───┴───────┐
     │           │
┌────▼────┐  ┌──▼──────────┐
│ CLI App │  │ Streamlit   │
│ app/    │  │   Web UI    │
│bairdqa_ │  │ app/bairdqa_│
│ cli.py  │  │  sl.py      │
└─────────┘  └─────────────┘
     │           │
     └─────┬─────┘
           │
      ┌────▼────────┐
      │   litellm   │  ← Unified LLM API
      └────┬────────┘
           │
      ┌────▼──────────────────────┐
      │   LLM Providers           │
      │ • Ollama (gemma3/gemma4)  │
      │ • Gemini 2.5 Flash        │
      │ • GPT-4                   │
      │ • Claude-3 Sonnet         │
      └───────────────────────────┘
```

## Conclusion

The organized structure provides:
- ✅ Clear separation of concerns
- ✅ Maintainable codebase
- ✅ Easy testing
- ✅ Scalable design
- ✅ Unified LLM access via litellm
