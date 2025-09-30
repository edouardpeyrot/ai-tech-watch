#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cron-friendly script:
- Calls OpenAI Chat Completions
- Sends an email via SMTP (Amazon SES supported)

Crontab examples (UTC):
  # Every Monday 08:00
  0 8 * * 1 /usr/bin/env python3 /path/main.py --frequency week --stack "Python/FastAPI" --topics FastAPI Pydantic
  # Daily 08:00
  0 8 * * * /usr/bin/env python3 /path/main.py --frequency day --stack "Data/ML"
"""
import hashlib
import os
import sys
import argparse
import json
from email.mime.image import MIMEImage
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
import requests
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

def _read_env(name: str, required: bool = False, default: str | None = None) -> str | None:
    val = os.getenv(name, default)
    if required and not val:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(2)
    return val


def build_system_prompt(system_prompt: str, frequency: str) -> str:
    short_format = "YYYY-WW" if frequency == "week" else "YYYY-MM"
    return system_prompt.format(frequency=frequency, short_format=short_format)



def build_user_prompt(stack: list[str], topics: list[str] | None | None = None) -> str:
    msg = ("Today is {today}. Please generate the watch. Even if you are allowed to mention other relevant subjects and linked domains, please focus on the following: {stack}."
           .format(today=datetime.now().strftime('%Y-%m-%d'), stack=stack))
    if topics is not None:
        msg += "The topics I also like are: {topics}.".format(topics=topics)
    else:
        msg += "Generate the general watch for the requested period using official sources and reputable blogs."

    return msg


def call_openai_chat(model: str, system_prompt: str, user_prompt: str, temperature: float, api_base: str | None = None,
                     api_key: str | None = None) -> str:
    """
        OpenAI Chat Completions (non-streaming)
        - api_base default: https://api.openai.com/v1
        - model: e.g. 'gpt-4o-mini'
        """
    url = f"{api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=180)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        err_body = e.response.text if e.response else str(e)
        raise RuntimeError(f"API error {e.response.status_code if e.response else 'unknown'}: {err_body}") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {str(e)}") from e

    if "choices" in data and data["choices"]:
        msg = data["choices"][0].get("message") or {}
        return msg.get("content", "").strip()
    return json.dumps(data)


def download_image(url: str) -> tuple[bytes | None, str]:
    """
    Download an image from URL and return its binary data and content type.

    Returns:
        - (image_data, content_type) if successful
        - (None, '') if failed
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', 'image/jpeg')

        # Extract just the MIME type without parameters
        if ';' in content_type:
            content_type = content_type.split(';')[0].strip()

        return response.content, content_type
    except Exception as e:
        print(f"Warning: Failed to download image from {url}: {e}")
        return None, ''


def generate_cid_from_url(url: str) -> str:
    """
    Generate a unique Content-ID from an image URL using hash.
    """
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return f"image_{url_hash}"

def process_images_in_data(data: dict) -> tuple[dict, dict[str, tuple[bytes, str]]]:
    """
    Process all image URLs in the data structure, download them,
    and replace URLs with cid: references.

    Returns:
        - Modified data with cid: references
        - Dictionary mapping CID -> (image_data, content_type)
    """
    images_map = {}  # cid -> (image_data, content_type)

    def replace_image_url(url: str | None) -> str:
        if not url or not url.startswith('http'):
            return url or ''

        cid = generate_cid_from_url(url)

        # Download image if not already downloaded
        if cid not in images_map:
            image_data, content_type = download_image(url)
            if image_data:
                images_map[cid] = (image_data, content_type)
                return cid  # Return only the CID, template will add "cid:" prefix
            else:
                # If download fails, keep the original URL
                return url
        else:
            return cid  # Return only the CID, template will add "cid:" prefix

    # Process banner image
    if data.get('image'):
        data['image'] = replace_image_url(data['image'])

    # Process technologies images
    if data.get('technologies') and data['technologies'].get('details'):
        for item in data['technologies']['details']:
            if item.get('image'):
                item['image'] = replace_image_url(item['image'])

    # Process business images
    if data.get('business') and data['business'].get('details'):
        for item in data['business']['details']:
            if item.get('image'):
                item['image'] = replace_image_url(item['image'])

    return data, images_map

def render_email_html_with_jinja(subject: str, body_json: str, template_path: str = "email.j2", error_template_path:str = "error.j2") -> \
tuple[str, dict[Any, Any]] | tuple[str, Any]:
    """
    Renders the HTML email using a Jinja2 template (email.j2) from the model JSON.
    The JSON is expected to follow:
    {
      "week": "YYYY-WW",
      "image": "https://...",
      "technologies": { "summary": "...", "details": [ { "title": "...", "summary": "...", "source": "...", "date": "YYYY-MM-DD", "image": "..." } ] },
      "business": { "summary": "...", "details": [ { "title": "...", "summary": "...", "source": "...", "date": "YYYY-MM-DD", "image": "..." } ] }
    }
    """

    env = Environment(
        loader=FileSystemLoader(searchpath=os.getcwd()),
        autoescape=select_autoescape(enabled_extensions=("j2", "html"))
    )
    try:
        data = json.loads(body_json) if isinstance(body_json, str) else (body_json or {})
        if not isinstance(data, dict):
            raise ValueError("Root JSON must be an object")
    except Exception:
        # If JSON is invalid, render a minimal fallback with raw content
        tpl = env.get_template(error_template_path)
        return tpl.render(
            subject=subject,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
            raw_content=str(body_json),
        ), {}

    # Process and download images
    data, images_map = process_images_in_data(data)

    template = env.get_template(template_path)
    html_content = template.render(
        subject=subject,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        week=data.get("week"),
        image=data.get("image"),
        technologies=data.get("technologies") or {},
        business=data.get("business") or {},
    )

    return html_content, images_map



def send_email(smtp_host: str, smtp_port: int, smtp_user: str | None, smtp_password: str | None,
                   from_addr: str, to_addrs: list[str], subject: str, html_body: str,
                   images_map: dict[str, tuple[bytes, str]] | None = None):
        """
        Send email with inline images.

        Args:
            images_map: Dictionary mapping CID -> (image_data, content_type)
        """
        msg = MIMEMultipart("related")
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = ", ".join(to_addrs)

        # Add HTML content
        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html_body, "html", "utf-8"))

        # Attach inline images
        if images_map:
            for cid, (image_data, content_type) in images_map.items():
                # Determine image subtype from content_type
                subtype = content_type.split('/')[-1] if '/' in content_type else 'jpeg'
                if ';' in subtype:
                    subtype = subtype.split(';')[0]

                mime_image = MIMEImage(image_data, _subtype=subtype)
                mime_image.add_header('Content-ID', f'<{cid}>')
                mime_image.add_header('Content-Disposition', 'inline')
                msg.attach(mime_image)

        ses_host = os.getenv("SES_SMTP_HOST")  # e.g., email-smtp.eu-west-1.amazonaws.com
        ses_port = os.getenv("SES_SMTP_PORT")
        ses_user = os.getenv("SES_SMTP_USER")
        ses_pass = os.getenv("SES_SMTP_PASSWORD")

        host = ses_host or smtp_host
        port = int(ses_port or smtp_port or 587)
        user = ses_user or smtp_user
        password = ses_pass or smtp_password

        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=30) as server:
                if user and password:
                    server.login(user, password)
                server.sendmail(from_addr, to_addrs, msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=30) as server:
                server.ehlo()
                use_starttls = os.getenv("SMTP_STARTTLS", "true").lower() in ("1", "true", "yes", "on")
                if use_starttls:
                    server.starttls()
                    server.ehlo()
                if user and password:
                    server.login(user, password)
                server.sendmail(from_addr, to_addrs, msg.as_string())


def build_subject(stack: str, frequency: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d")
    return f"Tech watch {frequency} - {stack} - {now}"


def main():
    parser = argparse.ArgumentParser(description="Tech watch via OpenAI -> Email")
    parser.add_argument("--dry-run", action="store_true", help="Print instead of sending")
    args = parser.parse_args()

    api_key = _read_env("OPENAI_API_KEY", required=True)
    api_base = _read_env("OPENAI_BASE_URL")

    config = yaml.safe_load(open("config.yaml"))
    system_prompt = build_system_prompt(config['system_prompt'], config['frequency'])
    user_prompt = build_user_prompt(config['topics'])

    content = call_openai_chat(
        model=config['model'],
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        api_base=api_base,
        api_key=api_key,
        temperature=config['temperature']
    )

    subject = build_subject(config.get('stack'), config.get('frequency'))

    # SMTP config (SES supported via SES_* env vars)
    smtp_host = _read_env("SMTP_HOST", default="email-smtp.eu-west-1.amazonaws.com")
    smtp_port = int(_read_env("SMTP_PORT", default="587"))
    smtp_user = _read_env("SMTP_USER")
    smtp_password = _read_env("SMTP_PASSWORD")

    from_addr = _read_env("MAIL_FROM", required=True)
    to_addrs_env = _read_env("MAIL_TO", required=True)  # comma-separated
    to_addrs = [x.strip() for x in to_addrs_env.split(",") if x.strip()]

    html_body, images_map = render_email_html_with_jinja(subject, content)

    print(f"Downloaded {len(images_map)} images for inline embedding")

    if args.dry_run:
        print(f"[DRY-RUN] Subject: {subject}")
        print(f"[DRY-RUN] Images embedded: {len(images_map)}")
        print(html_body)
        return

    send_email(smtp_host, smtp_port, smtp_user, smtp_password, from_addr, to_addrs, subject, html_body, images_map)


if __name__ == "__main__":
    main()