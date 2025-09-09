# autoFormer

A powerful Python automation script for bulk Google Forms submissions with intelligent field detection, file upload support, and built-in cooldown management.

## Features

🚀 **Bulk CSV Processing**: Process multiple form entries from a CSV file  
⏱️ **Smart Cooldown**: Configurable delay between submissions (default: 20 seconds)  
📎 **File Upload Support**: Handles Google Drive picker for file attachments  
🔐 **Google Login Integration**: Seamless authentication handling  
📊 **Progress Tracking**: Real-time progress with success/failure statistics  
⚙️ **Configurable Submission**: Enable/disable auto-submit functionality  
🛡️ **Robust Error Handling**: Comprehensive error catching and recovery

## Setup Instructions

### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. CSV File Preparation

Create a `data.csv` file with the following structure:

```csv
partner_email,student_email,date,flow_status,file_path
```

**Column Descriptions:**

- `partner_email`: Partner's email address
- `student_email`: Student's email address
- `date`: Date in YYYY-MM-DD format
- `flow_status`: One of "Yes", "No", or "Not sure"
- `file_path`: Optional file path for upload (leave empty if no file)

### 3. Configuration

Edit the configuration variables in `autoFormer.py`:

```python
AUTO_SUBMIT = True  # Set to False to review forms before submission
COOLDOWN_SECONDS = 20  # Wait time between submissions
CSV_FILE_PATH = "./form_data.csv"  # Path to your CSV file
```

## Usage

1. **Start the script:**

   ```bash
   python autoFormer.py
   ```

2. **Login when prompted:**

   - Script will open Chrome and navigate to the form
   - If Google login is required, log in manually
   - Press Enter when you see the form loaded

3. **Monitor progress:**
   - Watch real-time processing of each entry
   - View success/failure status for each submission
   - Final summary shows overall statistics

## Technical Details

### Dependencies

- **Selenium WebDriver**: Browser automation
- **ChromeDriverManager**: Automatic driver management
- **pandas**: CSV file processing
- **Python 3.7+**: Required Python version

### Form Field Detection

The script uses intelligent selectors to detect:

- Email input fields (partner and student)
- Date picker fields
- Radio button selections
- File upload buttons with Google Drive integration

### Error Handling

- **Missing files**: Gracefully skips file upload if file not found
- **Network issues**: Retries and continues with next entry
- **Element detection**: Falls back to alternative selectors
- **Session management**: Maintains browser state across submissions

## Example Output

```text
🚀 Starting bulk form automation...
📊 Total entries to process: 3
⏱️ Cooldown between submissions: 20 seconds

============================================================
📝 Processing entry 1/3
👤 Student: student1@example.com
📧 Partner: 23csjay072@ldce.ac.in
📅 Date: 2025-09-06
✅ Status: Yes
============================================================
✅ Filled Partner Email: 23csjay072@ldce.ac.in
✅ Filled Student Email: student1@example.com
✅ Filled Date: 2025-09-06
✅ Selected radio option: Yes
✅ Form submitted successfully!
✅ Entry 1 processed successfully!

⏳ Waiting 20 seconds before next submission...
```

## Troubleshooting

### Common Issues

- **Chrome crashes**: Handled automatically with optimized Chrome options
- **Login timeouts**: Manual intervention supported with prompts
- **File upload failures**: Graceful fallback with manual upload suggestion
- **Element not found**: Multiple selector fallbacks implemented

### Advanced Configuration

For custom forms, update the CSS selectors in the `fill_form_generic()` function to match your specific form structure.

## Safety Features

- **Rate limiting**: Built-in cooldown prevents server overload
- **Manual review**: Optional form review before submission
- **Error recovery**: Continues processing even if individual entries fail
- **Session persistence**: Maintains login across multiple submissions
