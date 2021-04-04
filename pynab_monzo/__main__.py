import os

from .app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"
    if port == 5000:
        host = "127.0.0.1"
    app.run(host=host, port=port)
