"""
train_chatbot.py
Run this script to train and save the chatbot intent classifier.

Usage (from the backend/services directory):
    py train_chatbot.py

Usage (from the project root):
    py backend/services/train_chatbot.py
"""

import sys
import os

# Allow running from project root OR from backend/services directly
_this_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_this_dir, "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Import using absolute package path (works when run from project root)
# Fall back to relative import when run directly from backend/services/
try:
    from backend.services.chatbot_ml_trainer import train_and_save
except ModuleNotFoundError:
    # Running directly: add backend/services to path
    sys.path.insert(0, _this_dir)
    from chatbot_ml_trainer import train_and_save

if __name__ == "__main__":
    print("=" * 55)
    print("  AI Financial Analyst — Chatbot Model Trainer")
    print("=" * 55)
    accuracy = train_and_save()
    print("=" * 55)
    print(f"  Model trained with accuracy: {accuracy:.1%}")
    print("=" * 55)
