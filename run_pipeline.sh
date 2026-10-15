cd "/Users/minhnn/Data/Data Engineer/big_project_1" || exit 1
export GOOGLE_APPLICATION_CREDENTIALS="/Users/minhnn/Data/Data Engineer/big_project_1/bigquery_key.json"
.venv/bin/python3 main.py >> logs/cron.log 2>&1