from players.models import Player
import json
import os

# Get the path of players.json
BASE_DIR = os.path.dirname(os.path.abspath(__name__))
json_path = os.path.join(BASE_DIR, "players.json")

# Load JSON data
with open(json_path) as f:
    data = json.load(f)

# Create Player objects
for p in data:
    Player.objects.create(**p)

print(f"Imported {len(data)} players successfully!")
