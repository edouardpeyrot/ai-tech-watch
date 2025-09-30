# 🤖 AI Tech Watch

> ⚠️ **Beta Version** - This project is under active development and may contain bugs. Use at your own risk.

Automated technology monitoring system using OpenAI API to generate weekly or daily reports sent via email with inline images.

## ✨ Features

- 🤖 Automatic content generation via OpenAI (GPT-4, GPT-4o-mini, etc.)
- 📧 Stylized HTML emails with embedded inline images (CID)
- 🎨 Customizable Jinja2 templates
- ⚙️ Simple YAML configuration
- 🔄 Cron-compatible for automation
- 📦 Precompiled binaries available (Windows, Linux, macOS)
- 🔐 SMTP/SMTP SSL/TLS and Amazon SES support

## 📥 Installation

### Option 1: Download Precompiled Binary (Recommended)

1. Go to the [Releases](https://github.com/YOUR_USERNAME/ai-tech-watch/releases) page
2. Download the version matching your system:
   - `ai-tech-watch-linux-amd64` for Linux
   - `ai-tech-watch-macos-amd64` for macOS
   - `ai-tech-watch-windows-amd64.exe` for Windows

3. Make the binary executable (Linux/macOS):
   ```bash
   chmod +x ai-tech-watch-linux-amd64
   # or
   chmod +x ai-tech-watch-macos-amd64
   ```

4. Place it in a folder of your choice:
   ```bash
   mkdir -p ~/ai-tech-watch
   mv ai-tech-watch-* ~/ai-tech-watch/
   cd ~/ai-tech-watch
   ```

### Option 2: Install from Source with Python

#### Prerequisites
- Python 3.13+ (tested with 3.13.5)
- pip
- virtualenv (recommended)

#### Installation Steps

```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/ai-tech-watch.git](https://github.com/YOUR_USERNAME/ai-tech-watch.git) cd ai-tech-watch
# Create and activate a virtual environment
python3 -m venv .venv source .venv/bin/activate # Linux/macOS
# or
.venv\Scripts\activate # Windows
# Install dependencies
pip install -r requirements.txt

```


## ⚙️ Configuration

### 1. Create the `.env` file

Create a `.env` file at the project root:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_API_KEY 
OPENAI_BASE_URL=[https://api.openai.com/v1](https://api.openai.com/v1)
# Email Configuration
MAIL_FROM=your-email@example.com 
MAIL_TO=recipient@example.com
# Multiple recipients separated by commas:
# MAIL_TO=user1@example.com,user2@example.com
# SMTP Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com 
SMTP_PORT=587 
SMTP_USER=your-email@example.com 
SMTP_PASSWORD=your_app_password
# Optional: Amazon SES SMTP (takes priority over SMTP_* if set)
# SES_SMTP_HOST=email-smtp.eu-west-1.amazonaws.com
# SES_SMTP_PORT=587
# SES_SMTP_USER=YOUR_SES_USER
# SES_SMTP_PASSWORD=YOUR_SES_PASSWORD
# Optional: SMTP Options
# SMTP_STARTTLS=true # Use STARTTLS (default: true)

```

### 2. Configure `config.yaml`

The `config.yaml` file contains the watch configuration:

```yaml

yaml model: "gpt-4o-mini" 
# Options: "gpt-4", "gpt-4o", "gpt-3.5-turbo" 
temperature: 0.7 # Creativity level (0.0 = precise, 1.0 = creative) 
max_tokens: 10000 # Maximum response length 
stack: DevOps / MLOps / AI / Cloud / Cybersecurity 
topics: Terraform / Kubernetes / AWS / Azure / GCP 
frequency: week # "week" for weekly, "month" for monthly
system_prompt: | You are an assistant specialized in {frequency} monitoring of AI, Cloud, DevOps and Cybersecurity news. Your mission is to produce the {frequency} technology and business watch.

#Constraints:
#Output must be in valid JSON only (no text outside JSON).
#All text content must be in English (or your preferred language).
#Structure required: {{ "week": "{short_format}", "image": "https://...", "technologies": {{ "summary": "...", "details": }}, "business": {{ "summary": "...", "details": }} }}
#Rules:
"week" = ISO week number (e.g. 2025-39) or date (YYYY-MM-DD).
Each "details" array = 3 to 10 items maximum.
"summary" = short synthesis (3-5 sentences max) for the period in that category.
"title" = concise name of the technology or business event.
"summary" (inside details) = explanation from 100 to 500 words.
"source" = exact URL of the article or reference site.
"date" = publication date (YYYY-MM-DD HH:MM).
"image" = URL of a relevant image from the internet (e.g., official press release, product logo, blog illustration).
No speculation or personal opinion, only facts.****
```


**Configuration Parameters:**

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `model` | OpenAI model to use | `gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo` |
| `temperature` | Response creativity (0.0-1.0) | `0.7` (balanced) |
| `max_tokens` | Maximum response length | `10000` |
| `stack` | Main technology domains | `DevOps / AI / Cloud` |
| `topics` | Specific topics of interest | `Kubernetes / AWS / Docker` |
| `frequency` | Report frequency | `week` or `day` |
| `system_prompt` | Instructions for the AI | See example above |

**Tips for customization:**
- Adjust `temperature` lower (0.3-0.5) for more factual content
- Increase `max_tokens` if you need longer reports
- Modify `system_prompt` to change the output language or format
- Add or remove topics based on your interests

### 3. Customize Templates (Optional)

You can personalize the email appearance by editing the Jinja2 templates:

- **`email.j2`**: Main HTML template for successful reports
  - Modify colors, fonts, layout
  - Add your company logo or branding
  - Adjust the structure (sections, cards, etc.)

- **`error.j2`**: Error notification template
  - Customize error messages
  - Add contact information or support links

**Example customizations:**

```bash 
Dry-run mode (preview without sending)
./ai-tech-watch-linux-amd64 --dry-run
Normal execution (generates and sends email)
./ai-tech-watch-linux-amd64
```

On macOS: `bash ./ai-tech-watch-macos-amd64 --dry-run`

On Windows: `.\ai-tech-watch-windows-amd64.exe --dry-run`

#### With Python
``` bash

# Activate the virtual environment
source .venv/bin/activate # Linux/macOS
# or
.venv\Scripts\activate # Windows
# Dry-run mode
python main.py --dry-run
# Normal execution
python main.py

```


**What happens during execution:**
1. Reads configuration from `config.yaml` and `.env`
2. Calls OpenAI API to generate content
3. Downloads and embeds images inline
4. Renders HTML email from template
5. Sends email via SMTP (or shows preview in dry-run mode)

### Automation with Cron

Automate report generation using cron (Linux/macOS) or Task Scheduler (Windows).

#### 1. With the Binary

``` bash 
Edit crontab
crontab -e
Weekly execution (every Monday at 8:00 AM)
0 8 * * 1 cd /path/to/ai-tech-watch && ./ai-tech-watch-linux-amd64 >> /tmp/ai-tech-watch.log 2>&1
Daily execution (every day at 8:00 AM)
0 8 * * * cd /path/to/ai-tech-watch && ./ai-tech-watch-linux-amd64 >> /tmp/ai-tech-watch.log 2>&1

```

#### 2. With Python and Virtual Environment

``` bash 
bash crontab -e
# Weekly (Mondays at 8:00 AM)
0 8 * * 1 cd /path/to/ai-tech-watch && /path/to/ai-tech-watch/.venv/bin/python main.py >> /tmp/ai-tech-watch.log 2>&1
# Daily (every day at 8:00 AM)
0 8 * * * cd /path/to/ai-tech-watch && /path/to/ai-tech-watch/.venv/bin/python main.py >> /tmp/ai-tech-watch.log 2>&1
```

