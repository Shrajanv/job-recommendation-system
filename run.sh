#!/bin/bash
echo "=== JobReco Setup ==="

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python3 database/setup_db.py
python3 -c "from model.recommender import train_model; train_model()"

echo ""
echo "=== Setup done! Starting app... ==="
echo "Open http://127.0.0.1:5000 in your browser"
python3 app.py
