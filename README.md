# Gram-Vani 🎙️

A voice-first RAG (Retrieval-Augmented Generation) application for making government documents accessible through voice interaction in Indian languages.

## Features

- 🎤 **Voice Input**: Ask questions using your voice in multiple Indian languages
- 📄 **PDF Upload**: Upload government documents for processing
- 🌐 **Multi-language Support**: Hindi, English, Tamil, Telugu, Bengali, and more
- 🔊 **Voice Output**: Receive simplified answers as voice responses
- 🤖 **AI-Powered**: Uses AWS Bedrock (Claude 3.5 Sonnet) for intelligent document understanding
- 🗣️ **AWS Audio Services**: Amazon Transcribe for STT and Amazon Polly for TTS with Indian voices

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <[repository-url](https://github.com/mahimasisodiya049-blip/Gram_vani)>
cd gram-vani
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (create a `.env` file):
```bash
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
```

See [SETUP_CREDENTIALS.md](SETUP_CREDENTIALS.md) for detailed setup instructions.

### Running the Application

Start the Streamlit app:

```bash
# Basic version
streamlit run app.py

# Improved version with full audio flow
streamlit run app_improved.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

1. **Upload Documents**: 
   - Click on the PDF upload zone on the right
   - Select one or more government PDF documents
   - Click "Process Documents" to index them

2. **Select Language**:
   - Choose your preferred language from the dropdown

3. **Ask Questions**:
   - Click the microphone button to record your question
   - Speak clearly in your selected language
   - Click "Process Question" to get an answer

4. **Receive Answers**:
   - View the transcribed question
   - Read or listen to the simplified answer

## Project Structure

```
gram-vani/
├── app.py                      # Streamlit UI application (basic)
├── app_improved.py             # Streamlit UI with full audio flow
├── models/                     # Data models
│   ├── document.py            # Document and chunk models
│   ├── query.py               # Query result models
│   └── responses.py           # API response models
├── integrations/              # External service integrations
│   ├── bhashini_client.py    # Bhashini ULCA API client (legacy)
│   ├── aws_client.py         # AWS Bedrock RAG client
│   ├── aws_audio_client.py   # AWS Transcribe & Polly client
│   └── README.md             # Integration documentation
├── tests/                     # Test suite
│   ├── test_models_unit.py   # Unit tests
│   └── test_models_properties.py  # Property-based tests
├── examples/                  # Usage examples
│   └── bhashini_example.py   # Bhashini client example
├── .kiro/specs/gram-vani/    # Feature specifications
│   ├── requirements.md       # Requirements document
│   ├── design.md            # Design document
│   └── tasks.md             # Implementation tasks
├── SETUP_CREDENTIALS.md      # Credential setup guide
├── AWS_MIGRATION.md          # AWS audio services migration guide
└── requirements.txt          # Python dependencies
```

## Technology Stack

- **Frontend**: Streamlit
- **Speech-to-Text**: Amazon Transcribe (supports Hindi, English, Tamil, Telugu, Bengali)
- **Text-to-Speech**: Amazon Polly (Aditi/Madhav voices for Hindi)
- **AI/ML**: AWS Bedrock (Claude 3.5 Sonnet for RAG)
- **Storage**: AWS S3 (document storage and Transcribe temp files)
- **Vector Database**: AWS OpenSearch Serverless / Pinecone (planned)
- **Testing**: pytest, Hypothesis (property-based testing)

## Development

### Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run only unit tests:
```bash
pytest tests/test_models_unit.py -v
```

Run only property-based tests:
```bash
pytest tests/test_models_properties.py -v
```

### Code Structure

The project follows a modular architecture:

- **Models**: Data structures and validation logic
- **Integrations**: External API clients (AWS Transcribe, Polly, Bedrock)
- **Services**: Business logic (document processing, RAG engine)
- **API**: FastAPI endpoints (to be implemented)
- **UI**: Streamlit interface

## Configuration

### AWS Setup

1. **Create an AWS account** at https://aws.amazon.com/
2. **Set up IAM user** with programmatic access
3. **Enable required services**:
   - Amazon Transcribe (STT)
   - Amazon Polly (TTS)
   - Amazon Bedrock (Claude 3.5 Sonnet)
   - Amazon S3 (storage)
4. **Configure IAM permissions** (see [SETUP_CREDENTIALS.md](SETUP_CREDENTIALS.md))
5. **Add credentials** to `.env` file or Streamlit secrets

For detailed setup instructions, see [SETUP_CREDENTIALS.md](SETUP_CREDENTIALS.md).

### Migration from Bhashini

If you're migrating from Bhashini to AWS audio services, see [AWS_MIGRATION.md](AWS_MIGRATION.md) for a complete guide.

## Supported Languages

| Language | Transcribe | Polly Voice | Status |
|----------|-----------|-------------|---------|
| Hindi (हिंदी) | ✅ hi-IN | Aditi (F), Madhav (M) | Full support |
| English | ✅ en-US | Joanna (F) | Full support |
| Tamil (தமிழ்) | ✅ ta-IN | Joanna (fallback) | STT only |
| Telugu (తెలుగు) | ✅ te-IN | Joanna (fallback) | STT only |
| Bengali (বাংলা) | ✅ bn-IN | Joanna (fallback) | STT only |
| Marathi (मराठी) | ⚠️ Fallback | Joanna (fallback) | Limited |
| Gujarati (ગુજરાતી) | ⚠️ Fallback | Joanna (fallback) | Limited |
| Kannada (ಕನ್ನಡ) | ⚠️ Fallback | Joanna (fallback) | Limited |

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

[To be determined]

## Acknowledgments

- **AWS**: For cloud infrastructure, Transcribe, Polly, and Bedrock services
- **Digital India**: For the vision of accessible government services
- **Streamlit**: For the rapid UI development framework

## Support

For issues and questions:
- Create an issue on GitHub
- Contact the development team

---

Built with ❤️ for Digital India 🇮🇳
