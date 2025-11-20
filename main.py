import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import auth_controller, product_controller, cart_controller, profile_controller, payment_controller, subscription_controller

app = FastAPI(
    description="Ecommerce Backend",
    title="ECOM",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(auth_controller.router, prefix="/api/v1")
app.include_router(product_controller.router, prefix="/api/v1/product")
app.include_router(cart_controller.router, prefix="/api/v1/cart")
app.include_router(profile_controller.router, prefix="/api/v1")
app.include_router(payment_controller.router, prefix="/api/v1/payment")
app.include_router(subscription_controller.router, prefix="/api/v1/subscribe")

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)

@app.get("/")
def read_root():
    return {"message": "app is running."}