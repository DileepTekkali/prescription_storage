import os
import uuid
from functools import wraps
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, send_from_directory, session, url_for
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "prescriptions")
SUPABASE_STORAGE_TIMEOUT = float(os.getenv("SUPABASE_STORAGE_TIMEOUT", "10"))
SUPABASE_DB_TIMEOUT = float(os.getenv("SUPABASE_DB_TIMEOUT", "20"))
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")

supabase_options = ClientOptions(
    postgrest_client_timeout=SUPABASE_DB_TIMEOUT,
    storage_client_timeout=SUPABASE_STORAGE_TIMEOUT,
)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, options=supabase_options)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
PUBLIC_DIR = os.path.join(app.root_path, "public")
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_MB * 1024 * 1024


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_public_url(storage_path: str) -> str:
    safe_path = quote(storage_path, safe="/")
    return f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/public/{SUPABASE_STORAGE_BUCKET}/{safe_path}"


def upload_to_storage(storage_path: str, file_bytes: bytes, content_type: str) -> None:
    safe_path = quote(storage_path, safe="/")
    upload_url = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/{SUPABASE_STORAGE_BUCKET}/{safe_path}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": content_type,
        "x-upsert": "false",
    }

    try:
        response = httpx.post(upload_url, headers=headers, content=file_bytes, timeout=SUPABASE_STORAGE_TIMEOUT)
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise RuntimeError("Upload timed out while connecting to Supabase Storage.") from exc
    except httpx.HTTPStatusError as exc:
        details = ""
        try:
            payload = exc.response.json()
            details = payload.get("message") or payload.get("error") or ""
        except ValueError:
            details = exc.response.text.strip()
        details = details[:180] if details else "Unexpected storage error."
        raise RuntimeError(f"Storage rejected upload ({exc.response.status_code}): {details}") from exc
    except httpx.HTTPError as exc:
        raise RuntimeError("Could not connect to Supabase Storage. Check network and SUPABASE_URL.") from exc


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/style.css")
def style_css():
    return send_from_directory(PUBLIC_DIR, "style.css")


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(_exc):
    flash(f"File too large. Maximum allowed size is {MAX_UPLOAD_SIZE_MB}MB.", "error")
    return redirect(url_for("dashboard"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip()
        age_raw = request.form.get("age", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not username or not age_raw or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if not email.endswith("@gmail.com"):
            flash("Please use a Gmail address.", "error")
            return redirect(url_for("register"))

        try:
            age = int(age_raw)
            if age <= 0:
                raise ValueError
        except ValueError:
            flash("Age must be a valid positive number.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("register"))

        try:
            existing = supabase.table("users").select("id").eq("email", email).limit(1).execute()
            if existing.data:
                flash("Email is already registered.", "error")
                return redirect(url_for("register"))

            result = supabase.table("users").insert(
                {
                    "email": email,
                    "username": username,
                    "age": age,
                    "password_hash": generate_password_hash(password),
                }
            ).execute()

            if not result.data:
                flash("Unable to register user.", "error")
                return redirect(url_for("register"))

            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        except Exception as exc:
            flash(f"Registration failed: {exc}", "error")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for("login"))

        try:
            result = (
                supabase.table("users")
                .select("id,email,username,age,password_hash")
                .eq("email", email)
                .limit(1)
                .execute()
            )

            if not result.data:
                flash("Invalid email or password.", "error")
                return redirect(url_for("login"))

            user = result.data[0]
            if not check_password_hash(user["password_hash"], password):
                flash("Invalid email or password.", "error")
                return redirect(url_for("login"))

            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["username"] = user["username"]
            session["age"] = user["age"]

            return redirect(url_for("dashboard"))
        except Exception as exc:
            flash(f"Login failed: {exc}", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/upload", methods=["POST"])
@login_required
def upload_prescription():
    prescription_date = request.form.get("prescription_date", "").strip()
    image = request.files.get("image")

    if not prescription_date:
        flash("Please select a date.", "error")
        return redirect(url_for("dashboard"))

    if image is None or image.filename == "":
        flash("Please choose an image file.", "error")
        return redirect(url_for("dashboard"))

    if not allowed_file(image.filename):
        flash("Only PNG, JPG, JPEG, or WEBP files are allowed.", "error")
        return redirect(url_for("dashboard"))

    file_name = secure_filename(image.filename)
    storage_path = f"{session['user_id']}/{uuid.uuid4().hex}_{file_name}"

    try:
        file_bytes = image.read()
        if not file_bytes:
            flash("Uploaded file is empty.", "error")
            return redirect(url_for("dashboard"))

        upload_to_storage(storage_path, file_bytes, image.mimetype or "application/octet-stream")
        public_url = build_public_url(storage_path)

        supabase.table("prescriptions").insert(
            {
                "user_id": session["user_id"],
                "prescription_date": prescription_date,
                "image_path": storage_path,
                "image_url": public_url,
            }
        ).execute()

        flash("Prescription uploaded successfully.", "success")
    except Exception as exc:
        flash(f"Upload failed: {exc}", "error")

    return redirect(url_for("dashboard"))


@app.route("/prescriptions")
@login_required
def prescriptions():
    items = []
    try:
        result = (
            supabase.table("prescriptions")
            .select("id,prescription_date,image_url,created_at,users(username,email,age)")
            .order("prescription_date", desc=True)
            .execute()
        )
        items = result.data or []
    except Exception as exc:
        flash(f"Could not fetch prescriptions: {exc}", "error")

    return render_template("prescriptions.html", prescriptions=items)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
