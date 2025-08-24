# AI Blueprint Generator

An AI-powered architectural blueprint generation system that creates and optimizes building floor plans using the Google Gemini API.

## Features

- Generate architectural blueprints for multiple building types
- Interactive visualization of floor plans
- Multi-floor support with floor switching
- Real-time design iteration based on feedback
- Design optimization for specific goals
- Wheelchair accessibility compliance
- Support for various building types:
  - Residential houses
  - Apartment complexes
  - Office buildings
  - Hospitals
  - Schools
  - And more...

## Installation

1. Clone the repository:
```sh
git clone <repository-url>
cd floorplanner
```

2. Install dependencies:
```sh
pip install -r requirements.txt
```

3. Set up your Google Gemini API key:
```sh
export GEMINI_API_KEY="your-api-key-here"
```

## Usage

1. Start the server:
```sh
python main.py
```

2. Open your browser and navigate to `http://localhost:8000`

3. Use the web interface to:
   - Select building type
   - Set requirements (area, floors, etc.)
   - Generate blueprints
   - Iterate on designs
   - Optimize for specific goals

## API Endpoints

- `GET /` - Main web interface
- `GET /api/building-types` - List available building types
- `POST /api/generate` - Generate initial blueprint
- `POST /api/iterate` - Update blueprint based on feedback
- `POST /api/update-floor` - Switch floor view
- `POST /api/optimize` - Optimize blueprint for specific goals
- `GET /api/history/{session_id}` - Get design iteration history

## Project Structure

```
├── main.py              # FastAPI server and main logic
├── prompt.py            # LLM prompt generation system
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html      # Web interface template
└── static/             # Static assets
```

## Technologies Used

- FastAPI - Web framework
- Google Gemini API - AI model for blueprint generation
- Jinja2 - Template engine
- Pydantic - Data validation
- HTML/CSS/JavaScript - Frontend interface

## Requirements

- Python 3.10+
- FastAPI
- Uvicorn
- Jinja2
- Pydantic
- Requests
- Python-multipart
- Aiofiles

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]