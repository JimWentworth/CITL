## Personal AI Coach (Streamlit)

A minimal Streamlit app that uses the OpenAI API (via the `OPENAL_APIKEY` environment variable) to provide persona-based coaching responses. All application logic lives in `app.py`; `prompts.py` only stores prompt templates and persona options, and `evaluation.py` runs three simple test cases against the prompt.

### Prerequisites

- **Python**: Install Python 3.10 or later from the official website (`https://www.python.org/downloads/`) or via a package manager (e.g. `brew install python` on macOS).
- **OpenAI API key**: You must have a valid API key and set it in the `OPENAL_APIKEY` environment variable.

### Create and activate a virtual environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

You should now see `(.venv)` in your shell prompt, indicating the virtual environment is active.

### Install dependencies

With the virtual environment active, install the required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Configure your OpenAI API key

Export your API key into the `OPENAL_APIKEY` environment variable (replace `your_api_key_here` with your actual key):

```bash
export OPENAL_APIKEY="your_api_key_here"  # macOS / Linux
```

On Windows (PowerShell):

```powershell
setx OPENAL_APIKEY "your_api_key_here"
```

After setting the variable, restart your terminal (if needed) so that `OPENAL_APIKEY` is available to the app.

### Run the Streamlit app

From the project root, with your virtual environment active and `OPENAL_APIKEY` set:

```bash
streamlit run app.py
```

This will start a local development server and open the Personal AI Coach interface in your browser.

### Run the evaluation script

To run three sample test cases against the prompt and print a short report to your terminal:

```bash
python evaluation.py
```

Make sure `OPENAL_APIKEY` is set before running the script.

