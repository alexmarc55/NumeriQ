import base64
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

def encode_image(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

def get_media_type(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        return "application/pdf"
    elif file_path.lower().endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    elif file_path.lower().endswith(".png"):
        return "image/png"
    raise ValueError(f"Tip de fisier neacceptat: {file_path}")


def call_openai_with_document(file_path: str, prompt: str, json_schema: dict) -> str:
    media_type = get_media_type(file_path)

    if media_type == "application/pdf":
        with open(file_path, "rb") as f:
            uploaded = client.files.create(file=f, purpose="user_data")
        content = [
            {"type": "file", "file": {"file_id": uploaded.id}},
            {"type": "text", "text": prompt},
        ]
    else:
        encoded = encode_image(file_path)
        content = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{media_type};base64,{encoded}"},
            },
            {"type": "text", "text": prompt},
        ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
        temperature=0.1,
        seed=42,
        response_format={
            "type": "json_schema",
            "json_schema": json_schema,
        },
    )
    return response.choices[0].message.content


def call_openai_text(prompt: str, json_schema: dict, model: str = "gpt-4o-mini") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        seed=42,
        response_format={
            "type": "json_schema",
            "json_schema": json_schema,
        },
    )
    return response.choices[0].message.content