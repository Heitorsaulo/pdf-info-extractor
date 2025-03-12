## PDF Information Extractor

This project is a FastAPI-based application that extracts text from PDF files, processes the text using OpenAI's API to extract relevant information, and generates an Excel file with the extracted data. The application includes a web interface for uploading PDF files and viewing the extracted information.

### Features

- **PDF Text Extraction**: Extracts text from uploaded PDF files.
- **Information Extraction**: Uses OpenAI's API to analyze the text and extract key points and summaries.
- **Excel Generation**: Creates an Excel file with the extracted information.
- **Web Interface**: Provides a user-friendly interface for uploading PDFs and viewing results.

### Technologies Used

- **FastAPI**: For building the backend API.
- **OpenAI API**: For processing and extracting information from the text.
- **Pandas**: For creating and formatting Excel files.

### Getting Started

1. Clone the repository:
    ```sh
    git clone https://github.com/Heitorsaulo/pdf-info-extractor.git
    cd pdf-info-extractor
    ```
2. Enter the project folder
   ```
   cd pdf-info-extractor
   ```
3. Configure your organization and project in the API_info.py file
   - Open the API_info.py file and set the values of self.organization and self.project with your account information

4. Create a virtual environment and install dependencies:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

5. Set up your OpenAI API key:
    ```sh
    export MY_OPENAI_KEY='your-openai-api-key'  # On Windows use `set MY_OPENAI_KEY=your-openai-api-key`
    ```

6. Run the application:
    ```sh
    uvicorn main:app --reload
    ```

7. Run the client:
    ```sh
    streamlit run .\pdf_extractor.py
    ```

8. Open your browser and navigate to `http://localhost:8501` to use the web interface.
