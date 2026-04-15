from fastapi import FastAPI


app = FastAPI()


@app.get(path="/")
def health_check() -> str:
    return "Worked"
