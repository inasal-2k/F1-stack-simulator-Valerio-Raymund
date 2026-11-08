import os
import secrets

from flask import Flask, flash, redirect, render_template, request, session, url_for

from queue_model import Queue


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)


@app.route("/")
def index():
    queue = Queue(session.get("queue_items", []))

    return render_template(
        "index.html",
        items=queue.items,
        size=queue.size(),
        removed=session.get("dequeued", []),
        highlight=request.args.get("peek") == "1",
    )


@app.route("/queue", methods=["POST"])
def operate():
    action = request.form.get("action", "").strip().lower()
    value = request.form.get("value", "").strip()

    queue = Queue(session.get("queue_items", []))
    removed = session.get("dequeued", [])
    highlight = False

    if action == "enqueue":
        if not value:
            flash("Enter a value before enqueueing it.", "error")
        elif len(value) > 24:
            flash("Values must be 24 characters or fewer.", "error")
        elif queue.size() >= 20:
            flash("The queue can hold up to 20 items.", "error")
        else:
            queue.enqueue(value)
            flash(f"Enqueued {value} at the rear of the queue.", "success")

    elif action == "dequeue":
        item = queue.dequeue()
        if item is None:
            flash("The queue is empty; there is nothing to dequeue.", "error")
        else:
            removed.insert(0, item)
            removed = removed[:20]
            flash(f"Dequeued {item} from the front of the queue.", "success")

    elif action == "peek":
        front = queue.peek()
        if front is None:
            flash("The queue is empty; there is nothing to peek at.", "error")
        else:
            highlight = True
            flash(f"The front item is {front}.", "success")

    elif action == "clear":
        queue.clear()
        removed = []
        flash("The queue and removed-item history have been cleared.", "success")

    else:
        flash("Unknown operation.", "error")

    session["queue_items"] = queue.items
    session["dequeued"] = removed

    if highlight:
        return redirect(url_for("index", peek="1"))

    return redirect(url_for("index"))


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run()