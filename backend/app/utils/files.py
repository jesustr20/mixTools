"""
Manejo de archivos temporales para todas las herramientas.
Cada request crea su propia carpeta aislada en tmp/<uuid>/.

IMPORTANTE: FileResponse es "perezoso" -> Starlette recién lee el archivo
DESPUÉS de que el endpoint retorna. Si borráramos la carpeta al salir de un
`with` (context manager clásico), el archivo desaparecería antes de poder
enviarse. Por eso aquí NO hay auto-borrado inmediato: se crea la carpeta con
new_workspace() y la limpieza se agenda con BackgroundTask (ver cleanup_task)
para que corra DESPUÉS de que la respuesta ya se envió al cliente.
"""
import shutil
import uuid
from pathlib import Path

from starlette.background import BackgroundTask

TMP_ROOT = Path(__file__).resolve().parents[2] / "tmp"
TMP_ROOT.mkdir(exist_ok=True)


def new_workspace() -> Path:
    """Crea y devuelve una carpeta temporal aislada para esta operación."""
    ws_path = TMP_ROOT / uuid.uuid4().hex
    ws_path.mkdir(parents=True, exist_ok=True)
    return ws_path


def cleanup_task(ws_path: Path) -> BackgroundTask:
    """Background task que borra la carpeta DESPUÉS de enviar la respuesta."""
    return BackgroundTask(shutil.rmtree, ws_path, ignore_errors=True)


def cleanup_now(ws_path: Path) -> None:
    """Borra la carpeta de inmediato (para los casos donde ya no se necesita
    el archivo en disco, p.ej. porque ya se leyó a memoria, o hubo un error
    antes de construir una respuesta perezosa)."""
    shutil.rmtree(ws_path, ignore_errors=True)


def save_upload(upload_file, dest_dir: Path) -> Path:
    """Guarda un UploadFile de FastAPI en disco y devuelve la ruta."""
    dest_path = dest_dir / upload_file.filename
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)
    return dest_path
