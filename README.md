# Medical Web Crawler Project

This project is a web application designed to generate therapeutic hypotheses given links to research. It utilizes FastAPI for the backend API, Next.js for the frontend, and OpenAI's large language model for hypothesis generation.

## Features

- Allows users to enter a research paper link.
- Scrapes the content of the research paper.
- Generates therapeutic hypotheses based on the extracted content.
- Stores the hypotheses and associated data in a database.
- Provides a unique UUID for each hypothesis for sharing and reference.

## Installation

### Backend (FastAPI)

1. Clone this repository:

    ```
    git clone git@github.com:sriragt/Medicine-WebCrawler.git
    ```

2. Navigate to the backend directory:

    ```
    cd backend
    ```

3. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

4. Set up environment variables:

    - `SUPABASE_URL`: URL of Supabase database.
    - `SUPABASE_KEY`: API key for Supabase database.
    - `TOGETHER_API_KEY`: API key for OpenAI's Together API.

5. Run the FastAPI server:

    ```
    python3 main.py
    ```

### Frontend (Next.js)

1. Navigate to the frontend directory:

    ```
    cd frontend
    ```

2. Install dependencies:

    ```
    npm install
    ```

3. Run the Next.js development server:

    ```
    npm run dev
    ```

## Usage

1. Access the application in your web browser by navigating to `http://localhost:3000`.
2. Enter a research paper link in the provided input field.
3. Submit the form to generate therapeutic hypotheses based on the content of the research paper.
