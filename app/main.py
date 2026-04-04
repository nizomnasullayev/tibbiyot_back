from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, topic, section, entry, user, upload, progress, test, certificate

app = FastAPI(title="My App")

app.router.redirect_slashes = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://tibbiyot-front.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(topic.router)
app.include_router(section.router)
app.include_router(entry.router)
app.include_router(upload.router)
app.include_router(progress.router)
app.include_router(test.router)
app.include_router(certificate.router)

@app.get("/")
def root():
    return {"message": "API is running"}