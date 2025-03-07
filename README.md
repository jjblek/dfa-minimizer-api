# DFA Minimizer API

## Overview

The Minimizer API is a Flask-based web service for minimizing Deterministic Finite Automata (DFA) using Hopcroft's algorithm. It accepts DFA representations in JSON format, processes them to remove unreachable and dead states, and returns an optimized, minimal equivalent DFA.

## Features

- Accepts DFA representations via a JSON request
- Removes unreachable and dead states
- Performs Hopcroft's minimization algorithm
- Returns a minimized DFA in JSON format
- Supports CORS for cross-origin requests

## Installation

### Prerequisites

Ensure you have Python installed (Python 3.x recommended).

### Setup

1. Clone the repository:

   ```sh
   git clone <your-repository-url>
   cd <your-repository-folder>
   ```

2. Create a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Running the API Locally

Start the Flask server:

```sh
python app.py
```

The API will be available at `http://127.0.0.1:5000/`

### API Endpoint

#### **Minimize DFA**

**Endpoint:** `POST /minimize`

**Description:**
Accepts a DFA JSON object and returns the minimized version.

**Request Body (JSON Example):**

```json
{
    "states": ["0", "1", "2"],
    "alphabet": ["a", "b"],
    "start": "0",
    "final": ["1"],
    "transitions": {
        "0": {"a": "1", "b": "2"},
        "1": {"a": "0", "b": "2"},
        "2": {"a": "2", "b": "2"}
    }
}
```

**Response Example:**

```json
{
    "states": ["01", "2"],
    "alphabet": ["a", "b"],
    "start": "01",
    "final": ["01"],
    "transitions": {
        "01": {"a": "01", "b": "2"},
        "2": {"a": "2", "b": "2"}
    }
}
```

### Deploying to AWS Lambda with Zappa

1. Install Zappa:

   ```sh
   pip install zappa
   ```

2. Initialize Zappa:

   ```sh
   zappa init
   ```

3. Deploy to AWS Lambda:

   ```sh
   zappa deploy
   ```

4. Update the deployment:

   ```sh
   zappa update
   ```

## License

This project is licensed under the MIT License.

## Author

Developed by Justin Blechel.
