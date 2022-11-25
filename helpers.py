from flask import render_template

def handle_error(message, code=400):
  """Render message in an error page to the user."""
  return render_template("error.html", code=code, message=message), code