#! /bin/sh

# Run the development server
uvicorn app.main:app --host 0.0.0.0 --port 80