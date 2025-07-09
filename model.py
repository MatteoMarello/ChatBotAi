import tkinter as tk
from tkinter import scrolledtext
import requests
import json

# Inserisci qui la tua API Key
API_KEY = "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"

# Funzione per inviare il messaggio all'AI
def send_message():
    user_input = user_entry.get()
    if not user_input.strip():
        return

    chat_log.insert(tk.END, "👤 Tu: " + user_input + "\n")
    user_entry.delete(0, tk.END)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 500,
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=headers, data=json.dumps(data))

        result = response.json()
        choice = result["choices"][0]
        ai_response = choice.get("message", {}).get("content", "").strip()
        reasoning = choice.get("message", {}).get("reasoning", "").strip()

        if ai_response:
            chat_log.insert(tk.END, "🤖 AI: " + ai_response + "\n\n")
        elif reasoning:
            chat_log.insert(tk.END, "🤖 AI (ragionamento): " + reasoning + "\n\n")
        else:
            chat_log.insert(tk.END, "⚠️ Nessuna risposta.\n\n")

        chat_log.see(tk.END)

    except Exception as e:
        chat_log.insert(tk.END, f"❌ Errore: {e}\n\n")

# Creazione finestra principale
root = tk.Tk()
root.title("Chat AI - DeepSeek via OpenRouter")

# Area chat
chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, font=("Arial", 10))
chat_log.pack(padx=10, pady=10)

# Campo input + bottone invio
user_entry = tk.Entry(root, width=50, font=("Arial", 12))
user_entry.pack(padx=10, pady=(0,10))
user_entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(root, text="Invia", command=send_message)
send_button.pack(pady=(0,10))

# Avvio app
root.mainloop()
