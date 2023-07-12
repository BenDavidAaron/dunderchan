#! /bin/sh

# Run the development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000