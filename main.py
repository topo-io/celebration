from fastapi import BackgroundTasks, FastAPI, Request
import subprocess
import stripe
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

endpoint_secret = os.getenv("STRIPE_ENDPOINT_SECRET")
stripe.api_key = os.getenv("STRIPE_API_KEY")


async def celebrate():
    print("Celebrating...")
    process = subprocess.Popen(
        ["vlc", "--intf", "dummy", "--play-and-exit", "gong.mp3"],
        stdout=subprocess.PIPE,
    )
    process.wait()
    print("Celebration completed!")


@app.post("/webhook")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(
        payload=payload,
        sig_header=sig_header,
        secret=endpoint_secret,
    )

    if event["type"] == "customer.subscription.created":
        print("Launching celebration asynchronously...")
        background_tasks.add_task(celebrate)

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
