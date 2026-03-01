# Gram-Vani 🎙️

A voice-first RAG (Retrieval-Augmented Generation) application for making government documents accessible through voice interaction in Indian languages.

## Features

- 🎤 **Voice Input**: Ask questions using your voice in multiple Indian languages
- 📄 **PDF Upload**: Upload government documents for processing
- 🌐 **Multi-language Support**: Hindi, English, Tamil, Telugu, Bengali, and more
- 🔊 **Voice Output**: Receive simplified answers as voice responses
- 🤖 **AI-Powered**: Uses AWS Bedrock for intelligent document understanding
- 🇮🇳 **Bhashini Integration**: Leverages Bhashini ULCA for Indian language speech processing

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gram-vani
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (create a `.env` file):
```bash
BHASHINI_API_KEY=your-bhashini-api-key
BHASHINI_USER_ID=your-bhashini-user-id
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
```

### Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
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
├── app.py                      # Streamlit UI application
├── models/                     # Data models
│   ├── document.py            # Document and chunk models
│   ├── query.py               # Query result models
│   └── responses.py           # API response models
├── integrations/              # External service integrations
│   ├── bhashini_client.py    # Bhashini ULCA API client
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
└── requirements.txt          # Python dependencies
```

## Technology Stack

- **Frontend**: Streamlit
- **Speech Processing**: Bhashini ULCA (STT/TTS)
- **AI/ML**: AWS Bedrock (Embeddings & LLM)
- **Storage**: AWS S3
- **Vector Database**: AWS OpenSearch Serverless / Pinecone
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
- **Integrations**: External API clients (Bhashini, AWS)
- **Services**: Business logic (document processing, RAG engine)
- **API**: FastAPI endpoints (to be implemented)
- **UI**: Streamlit interface

## Configuration

### Bhashini ULCA Setup

1. Register at [Bhashini Platform](https://bhashini.gov.in/)
2. Obtain your API key and User ID
3. Add credentials to `.env` file

### AWS Setup

1. Create an AWS account
2. Set up S3 bucket for document storage
3. Enable AWS Bedrock access
4. Configure IAM roles and permissions
5. Add credentials to `.env` file

## Supported Languages

- Hindi (हिंदी)
- English
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Bengali (বাংলা)
- Marathi (मराठी)
- Gujarati (ગુજરાતી)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)
- Punjabi (ਪੰਜਾਬੀ)
- Odia (ଓଡ଼ିଆ)
- Assamese (অসমীয়া)

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

- **Bhashini**: For providing Indian language speech processing APIs
- **AWS**: For cloud infrastructure and AI services
- **Digital India**: For the vision of accessible government services

## Support

For issues and questions:
- Create an issue on GitHub
- Contact the development team

---

Built with ❤️ for Digital India 🇮🇳
