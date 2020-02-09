import hashlib
import os
import re
import unicodedata

import flask
import markupsafe
import mistune
import securescaffold


def get_static_url_path():
    """Generate a version-specific path for serving static assets.

    This is a blunt approach to adding a cache-busting hash to static
    filenames, where the hash is updated when the static file has changed.

    For local development this returns "/static/dev". On App Engine, this
    returns "/static/xyz" where "xyz" is derived from the deployed version.

    This means you get static URLs which change for every deployed version, so
    you can configure static assets to be cached, but a new deployment will
    result in clients getting the latest version (assuming jinja templates use
    `{{ url_for("static", filename="my.css") }}` to reference assets).

    The final piece of the puzzle is configuring `app.yaml` to serve static
    assets with a hash in the path.
    """
    app_version = os.getenv("GAE_VERSION", "dev")

    if app_version == "dev":
        fingerprint = "dev"
    else:
        # 6 characters means we only take 3 bytes of the digest. Good enough!
        app_version = app_version.encode("ascii", errors="ignore")
        fingerprint = hashlib.md5(app_version).hexdigest()[:6]

    return f"/static/{fingerprint}"


static_url_path = get_static_url_path()
app = securescaffold.create_app(__name__, static_url_path=static_url_path)


@app.route("/")
def about():
    """One-page introduction to Secure Scaffold."""

    with open("README-secure-scaffold.md") as fh:
        m = mistune.Markdown(renderer=Anchors())
        readme = m.render(fh.read())
        readme = markupsafe.Markup(readme)

    context = {
        "page_title": "Secure Scaffold",
        "readme": readme,
    }

    return flask.render_template("about.html", **context)


@app.route("/csrf", methods=["GET", "POST"])
def csrf():
    """Demonstration of using CSRF to protect a form."""
    context = {
        "page_title": "CSRF protection",
        "message": "",
    }

    if flask.request.method == "POST":
        first_name = flask.request.form.get("first-name")

        if first_name:
            context["message"] = f"Hello {first_name}!"

    return flask.render_template("csrf.html", **context)


@app.route("/headers")
def headers():
    """Show HTTP headers for the request."""
    context = {
        "page_title": "App Engine request headers",
        "headers": list(flask.request.headers),
    }

    return flask.render_template("headers.html", **context)


class Anchors(mistune.Renderer):
    """Adds id attributes to <h*> elements."""

    def header(self, text, level, raw=None):
        name = self.choose_name(text)
        class_ = f"title is-{level}"

        return f'<h{level} id="{name}" class="{class_}">{text}</h{level}>'

    def choose_name(self, text):
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore")
        text = re.sub(r"[^\w\s-]", "", text.decode("ascii")).strip().lower()
        text = re.sub(r"[-\s]+", "-", text)

        return text
