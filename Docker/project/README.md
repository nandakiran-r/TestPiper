# Piper TTS - Malayalam Voice Setup

This project uses Piper TTS with Malayalam language support (Arjun medium voice).

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Create Virtual Environment

Create a virtual environment named `piper_env`:

```bash
python3 -m venv piper_env
```

### 2. Activate Virtual Environment

Activate the virtual environment:

**On Linux/macOS:**
```bash
source piper_env/bin/activate
```

**On Windows:**
```bash
piper_env\Scripts\activate
```

### 3. Install Dependencies

Once the virtual environment is activated, install the required packages:

```bash
pip install piper-tts
```

### 4. Download Model Files

Download the Malayalam (Arjun medium) voice model files from Hugging Face:

**Model Files Location:**
https://huggingface.co/rhasspy/piper-voices/tree/main/ml/ml_IN/arjun/medium

**Files to Download:**
- `ml_IN-arjun-medium.onnx` - The model file
- `ml_IN-arjun-medium.onnx.json` - The model configuration file

**Steps:**
1. Visit the link above
2. Download both files
3. Place them in the `models/` folder in your project directory

The final directory structure should look like:
```
PiperTest/
├── models/
│   ├── ml_IN-arjun-medium.onnx
│   ├── ml_IN-arjun-medium.onnx.json
├── piper_env/
├── main.py
└── README.md
```

## Usage


With the virtual environment activated and model files in place, you can run the Streamlit app:

```bash
streamlit run main.py
```

## Deactivating Virtual Environment

When you're done working on the project, deactivate the virtual environment:

```bash
deactivate
```

## Project Structure

```
PiperTest/
├── models/                          # Directory for model files
│   ├── ml_IN-arjun-medium.onnx     # Malayalam voice model
│   └── ml_IN-arjun-medium.onnx.json # Model configuration
├── piper_env/                       # Python virtual environment
├── main.py                          # Main Python script
└── README.md                        # This file
```

## Notes

- Make sure the virtual environment is always activated before running the project
- The model files are required for the TTS functionality to work
- Ensure you have sufficient disk space (model files can be large)

## Troubleshooting

If you encounter issues:

1. **Module not found errors:** Ensure the virtual environment is activated
2. **Model not found:** Verify that the model files are in the `models/` folder with correct naming
3. **Permission errors:** Make sure you have read access to the model files

## Additional Resources

- [Piper TTS Documentation](https://github.com/rhasspy/piper)
- [Piper Voices Repository](https://huggingface.co/rhasspy/piper-voices)
