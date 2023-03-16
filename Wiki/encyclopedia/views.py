from django.shortcuts import render
from markdown2 import Markdown
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def mdToHtml(entry):
    title = util.get_entry(entry)
    markdowner = Markdown()

    if title == None:
        return None
    else:
        return markdowner.convert(title)

def entry(request, entry):
    content = mdToHtml(entry)

    if content == None:
        return render(request, "encyclopedia/error.html", {
            "message": "This entry does not exist."
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": entry,
            "content": content
    })

def search(request):
    if request.method == "POST":
        query = request.POST["q"]
        content = mdToHtml(query)

        if content is not None:
            return render(request, "encyclopedia/entry.html", {
                "entry": query,
                "content": content
            })
        else:
            database = util.list_entries()
            results = []
            for entry in database:
                if query.lower() in entry.lower():
                    results.append(entry)
            return render(request, "encyclopedia/search.html", {
                "results": results
            })

def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        checkEntry = util.get_entry(title)

        if checkEntry == None:
            entryContent = request.POST["content"]
            util.save_entry(title, entryContent)
            content = mdToHtml(title)

            print(title)
            print(content)
            return render(request, "encyclopedia/entry.html", {
                "entry": title,
                "content": content
            })
        
        else:
            return render(request, "encyclopedia/error.html", {
                "message": "This entry already exists."
            })
    else:
        return render(request, "encyclopedia/create.html")
    
def edit(request):
    if request.method == "POST":
        entry = request.POST["entry"]
        content = util.get_entry(entry)
        return render(request, "encyclopedia/edit.html", {
            "entry": entry,
            "content": content
        })
    
    else:
        return render(request, "encyclopedia/index.html", {

        })
    
def save(request):
    if request.method == "POST":
        entry = request.POST["entry"]
        content = request.POST["content"]

        util.save_entry(entry, content)
        content = mdToHtml(entry)

        return render(request, "encyclopedia/entry.html", {
            "entry": entry,
            "content": content
        })
    else:
        return render(request, "encyclopedia/index.html")

def rand(request):
    entries = util.list_entries()
    rand = random.choice(entries)
    content = mdToHtml(rand)

    return render(request, "encyclopedia/entry.html", {
        "entry": rand,
        "content": content
    })
