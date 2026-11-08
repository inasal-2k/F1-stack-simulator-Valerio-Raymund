import os
import secrets

from flask import Flask, flash, redirect, render_template, request, session, url_for

from stack_model import Stack


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)


@app.route("/")
def index():
    stack = Stack(session.get("items", []))
    items = list(reversed(stack.items))

    return render_template(
        "index.html",
        items=items,
        size=stack.size(),
        popped=session.get("popped", []),
        highlight=request.args.get("peek") == "1",
    )


@app.route("/stack", methods=["POST"])
def operate():
    action = request.form.get("action", "").strip().lower()
    value = request.form.get("value", "").strip()

    stack = Stack(session.get("items", []))
    popped = session.get("popped", [])
    highlight = False

    if action == "push":
        if not value:
            flash("Enter a value before pushing it onto the stack.", "error")
        elif len(value) > 24:
            flash("Values must be 24 characters or fewer.", "error")
        elif stack.size() >= 20:
            flash("The stack can hold up to 20 items.", "error")
        else:
            stack.push(value)
            flash(f"Pushed {value} onto the stack.", "success")

    elif action == "pop":
        removed = stack.pop()
        if removed is None:
            flash("The stack is empty; there is nothing to pop.", "error")
        else:
            popped.insert(0, removed)
            popped = popped[:20]
            flash(f"Popped {removed} from the stack.", "success")

    elif action == "peek":
        top = stack.peek()
        if top is None:
            flash("The stack is empty; there is nothing to peek at.", "error")
        else:
            highlight = True
            flash(f"The top item is {top}.", "success")

    elif action == "clear":
        stack.clear()
        popped = []
        flash("The stack and removed-item history have been cleared.", "success")

    else:
        flash("Unknown operation.", "error")

    session["items"] = stack.items
    session["popped"] = popped

    if highlight:
        return redirect(url_for("index", peek="1"))

    return redirect(url_for("index"))


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run()