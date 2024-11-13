import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        timeout_keep_alive=65,
        log_level="info",
        server_header=False,
    )
