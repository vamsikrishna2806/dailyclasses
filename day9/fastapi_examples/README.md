# FastAPI sample programs

Every code example from `../fastapi_complete_tutorial.html`, one folder per section.
The code is copied straight from the HTML.

🎬 **Animated 3D lessons** for every example (kid-friendly, with What / Why / When / Where / How):
open `../fastapi_visual_guide/index.html` in your browser.

## 1. Set up the virtual environment (once)

```bat
cd D:\getwork\day8\fastapi_examples
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

The `.venv` is already created and installed. You only need `.venv\Scripts\activate`.

> **SQLModel on this PC:** Windows Smart App Control blocks SQLAlchemy's compiled files.
> If you reinstall packages and example 17 fails with "An Application Control policy has blocked this file", run:
>
> ```bat
> set DISABLE_SQLALCHEMY_CEXT=1
> pip install --force-reinstall --no-deps --no-binary sqlalchemy sqlalchemy
> ```

## 2. Run an example

Go into its folder, then start it:

```bat
cd 01_hello_world
fastapi dev main.py
```

**Or run the Python file itself.** Every example ends with this block:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
```

So these also work:

```bat
cd 01_hello_world
python main.py
```

- `13_security_oauth2_jwt`: `python auth_app.py`
- `16_apirouter_structure`: `cd myapi` then `python -m app.main` (it needs `-m` because it imports `app.routers`)

Press `Ctrl+C` to stop the server.

Open http://127.0.0.1:8000/docs to try every endpoint in the browser.

| Folder | HTML section | How to run |
|---|---|---|
| 01_hello_world | Your first app | `fastapi dev main.py` |
| 02_http_methods_crud | HTTP methods (CRUD) | `fastapi dev main.py` |
| 03_path_parameters | Path parameters | `fastapi dev main.py` |
| 04_query_parameters | Query parameters | `fastapi dev main.py` |
| 05_request_body_pydantic | Request body & Pydantic | `fastapi dev main.py` |
| 06_extra_validation | Extra validation (+ `models.py` custom validators) | `fastapi dev main.py` |
| 07_response_models | Response models | `fastapi dev main.py` |
| 08_status_codes_errors | Status codes & errors | `fastapi dev main.py` |
| 09_headers_cookies_forms_files | Headers, cookies, forms, uploads | `fastapi dev main.py` |
| 10_interactive_docs | Docs metadata | `fastapi dev main.py` |
| 11_async_await | async / await | `fastapi dev main.py` |
| 12_dependency_injection | Depends | `fastapi dev main.py` |
| 13_security_oauth2_jwt | OAuth2 + JWT (user `asha`, password `secret`) | `fastapi dev auth_app.py` |
| 14_middleware_cors | Middleware & CORS (no routes, check `/docs` headers) | `fastapi dev main.py` |
| 15_background_tasks | Background tasks (writes `emails.log`) | `fastapi dev main.py` |
| 16_apirouter_structure | APIRouter | `cd myapi` then `fastapi dev app/main.py` |
| 17_databases_sqlmodel | SQLModel (creates `heroes.db`) | `fastapi dev main.py` |
| 18_lifespan_settings | Lifespan & settings (reads `.env`) | `fastapi dev main.py` |
| 19_websockets_chat | WebSockets (test with `test_in_browser.js` in the browser console) | `fastapi dev main.py` |
| 20_responses_static_templates | Response types, static files, templates | `fastapi dev main.py` |
| 21_todo_api_mini_project | Todo API + tests + Dockerfile + curl commands | `fastapi dev main.py`, `pytest -v` |

## Changes from the HTML

- **04_query_parameters**: the HTML snippet has no imports, so `from fastapi import FastAPI` and `app = FastAPI()` were added at the top.
- **16_apirouter_structure**: the HTML only shows `users.py`, so a small `routers/items.py` and the `__init__.py` files were added.
- **20_responses_static_templates**: added `static/logo.png` (a tiny placeholder), because `StaticFiles` needs the folder to exist. `/report` needs a `report.pdf` you supply.
- **21_todo_api_mini_project/test_main.py**: the HTML imports `get_db`, which the Todo app does not have. The import was removed and the `dependency_overrides` example is kept as a comment.
- **07_response_models**: `/items/{id}` returns `...` exactly like the HTML, so calling it gives a 500 error. It is a placeholder.
