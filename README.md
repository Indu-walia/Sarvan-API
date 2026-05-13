# Sarvam API Test Suite

This project contains automated test scripts for testing the Sarvam AI translation API across various Indian languages. The tests are organized using the pytest framework.

## Project Structure

- `tests/`: Contains all test scripts
  - `test_add_cases.py`: Script to add new test cases to the Excel file
  - `test_sarvam_all_langs.py`: Tests translation across all supported languages
  - `test_sarvam_automation.py`: Automated testing script for the API
  - `test_sarvam_full_run.py`: Full test run script
- `requirements.txt`: Python dependencies
- `pytest.ini`: Pytest configuration (though scripts run directly)
- `Claude.md`: API documentation and examples
- `Final_With_New_Scenarios.xlsx`: Test data Excel file

## Setup

1. Install Python 3.9+.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Tests

### Run all scripts (not recommended for pytest due to script nature)
```bash
pytest tests/
```

### Run a specific script directly
```bash
python tests/test_add_cases.py
python tests/test_sarvam_all_langs.py
python tests/test_sarvam_automation.py
python tests/test_sarvam_full_run.py
```

### Run a specific test function (if converted to pytest format)
```bash
pytest tests/test_sarvam_full_run.py::test_sarvam_full_run
```

## API Configuration

The scripts use the Sarvam AI translation API. Ensure you have a valid API key configured in the scripts.

- API URL: https://api.sarvam.ai/translate
- Model: sarvam-translate:v1
- Supported languages: Assamese, Bengali, Bodo, Hindi, English, Dogri, Gujarati, Kannada, Kashmiri, Konkani, Maithili, Malayalam, Meitei, Marathi, Nepali, Odia, Punjabi, Sanskrit, Santali, Sindhi, Tamil, Telugu, Urdu

## Notes

- Test data is stored in `Final_With_New_Scenarios.xlsx`
- Results are typically output to Excel files in the download directory
- The scripts handle various edge cases including punctuation, numbers, and special characters in translations
- Scripts modify stdout encoding, so pytest may not work properly; run directly with python instead
- Use `BASE_URL` environment variable to override the default base URL if needed
