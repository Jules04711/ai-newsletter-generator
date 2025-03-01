# ai-newsletter-generator
AI Newsletter Generator is a Streamlit app that creates professional newsletters. Input a topic to generate a draft, refine content, and fetch recent news articles. Enhance engagement with lively content and export to Markdown. Utilizes local language models via Ollama and integrates with the News API for current information.

## Installation Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd <project-directory>
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure that [Ollama](https://ollama.com/) is running locally on `http://localhost:11434`.

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```
2. Use the web interface to input a newsletter topic and generate content.
3. Refine and enhance the generated content as needed.
4. Export the final newsletter to Markdown.

## Configuration

- The application uses environment variables for configuration. Create a `.env` file in the project root and add your News API key:
  ```
  NEWS_API_KEY=your_api_key_here
  ```
- Add your OLLAMA Model from https://ollama.com/:
  ```
  OLLAMA_MODEL= ENTER_OLLAMA_MODEL
  ```

## Features

- Generate AI and Data Analytics newsletters with structured content.
- Fetch recent news articles related to the topic.
- Refine and enhance newsletter content.
- Export newsletters to Markdown format.

## Dependencies

- `streamlit`
- `langchain`
- `requests`
- `python-dotenv`
- `Ollama` (ensure it is running locally)

## License

This project is licensed under the MIT License. See the LICENSE file for more details. 
