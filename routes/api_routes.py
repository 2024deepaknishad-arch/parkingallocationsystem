# routes/api_routes.py
from flask import Blueprint, request, jsonify
import requests, config, os

api_bp = Blueprint("api", __name__)

# Using a model that works with the current API
HF_URL = "https://api-inference.huggingface.co/models/gpt2"

@api_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    q = data.get("q", "").strip()
    if not q:
        return jsonify({"reply": "Ask a parking-related question."})
    
    # Format the prompt for better responses
    prompt = f"Answer this parking-related question concisely: {q}"
    
    headers = {"Authorization": f"Bearer {config.HF_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,
            "return_full_text": False,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.2
        },
        "options": {"wait_for_model": True}
    }
    
    try:
        print(f"Sending request to HF API: {HF_URL}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        
        r = requests.post(HF_URL, headers=headers, json=payload, timeout=30)
        
        print(f"HF API Status: {r.status_code}")
        print(f"HF API Response: {r.text[:500]}")
        
        # Handle different status codes
        if r.status_code == 404:
            return jsonify({"reply": "The AI model endpoint was not found. Please check the API configuration."})
        elif r.status_code == 401:
            return jsonify({"reply": "Unauthorized access to AI model. Please check the API key."})
        elif r.status_code == 429:
            return jsonify({"reply": "Rate limit exceeded. Please wait before making another request."})
        elif r.status_code >= 500:
            return jsonify({"reply": "AI service is temporarily unavailable. Please try again later."})
        
        r.raise_for_status()
        out = r.json()
        
        # Process the response
        text = ""
        if isinstance(out, list) and len(out) > 0:
            if isinstance(out[0], dict) and "generated_text" in out[0]:
                text = out[0]["generated_text"]
            else:
                text = str(out[0])
        elif isinstance(out, dict):
            if "generated_text" in out:
                text = out["generated_text"]
            else:
                text = str(out)
        else:
            text = str(out)
        
        # Clean and format the response
        # Remove the prompt from the response if it's included
        if text.startswith(prompt):
            text = text[len(prompt):].strip()
        
        reply = text.replace("\n", " ").strip()
        
        # Limit response length
        if len(reply) > 200:
            reply = reply[:197] + "..."
        
        # Handle empty or error responses
        if not reply or len(reply) < 2:
            return jsonify({"reply": "I can help with parking questions. Could you be more specific?"})
        
        # Handle model loading messages
        if "loading" in reply.lower() or "currently loading" in reply.lower():
            return jsonify({"reply": "The AI model is loading. Please try again in a moment."})
            
        return jsonify({"reply": reply})
    except requests.exceptions.Timeout:
        return jsonify({"reply": "The request timed out. Please try again."})
    except requests.exceptions.ConnectionError:
        return jsonify({"reply": "Could not connect to AI service. Please check your internet connection."})
    except requests.exceptions.RequestException as e:
        return jsonify({"reply": f"Network error: {str(e)}"})
    except Exception as e:
        print(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"reply": f"AI assistant unavailable. Please try again later."})