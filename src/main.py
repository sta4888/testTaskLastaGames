from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from starlette.templating import Jinja2Templates

from api.v1.start_endpoints import router as start
from api.v2.endpoints.start_endpoints import router as start_endpoints

from settings import settings

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title=settings.project.title,
    description=settings.project.description,
    version=settings.project.release_version,
    debug=settings.debug
)
Instrumentator().instrument(app).expose(
    app,
    endpoint="/api/v2/metrics",
    tags=["start"]
)

templates = Jinja2Templates(directory="templates")

app.include_router(start, prefix="/api/v1", tags=["old"])
app.include_router(start_endpoints, prefix="/api/v2", tags=["start"])


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def upload_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
