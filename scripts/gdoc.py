#!/usr/bin/env python3
"""Read and write a Google Doc through the Docs API, no browser involved.

  python3 scripts/gdoc.py structure <doc-id>
  python3 scripts/gdoc.py cell      <doc-id> <table> <row> <col>
  python3 scripts/gdoc.py set-cell  <doc-id> <table> <row> <col> <file>

Auth: a service account key at $GDOC_KEY, default ~/.hermes/secrets/gdocs-sa.json.
Share the Doc with the service account address as Editor, then the same script can
read the structure and write one cell at a time.

Rows and columns are 0-based; <table> counts tables in document order, also 0-based.
Writing keeps the paragraph style that is already in the cell, because insertText
inherits from the insertion point. It does not recreate bullet or numbering styles:
if a cell's bullets matter, write plain paragraphs and style them in the Doc.
"""
import json
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/documents"]
KEY = os.environ.get("GDOC_KEY", os.path.expanduser("~/.hermes/secrets/gdocs-sa.json"))


def service():
    if not os.path.exists(KEY):
        sys.exit("no key at %s — see the setup steps" % KEY)
    creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
    return build("docs", "v1", credentials=creds, cache_discovery=False)


def fetch(docs, doc_id):
    return docs.documents().get(documentId=doc_id).execute()


def tables(doc):
    out = []
    for el in doc.get("body", {}).get("content", []):
        if "table" in el:
            out.append(el["table"])
    return out


def cell_text(cell):
    parts = []
    for el in cell.get("content", []):
        if "paragraph" in el:
            for run in el["paragraph"].get("elements", []):
                if "textRun" in run:
                    parts.append(run["textRun"].get("content", ""))
    return "".join(parts)


def cmd_structure(docs, doc_id):
    doc = fetch(docs, doc_id)
    print("title:", doc.get("title"))
    for ti, t in enumerate(tables(doc)):
        rows = t.get("tableRows", [])
        print("table %d — %d rows × %d cols" % (ti, len(rows), t.get("columns", "?")))
        for ri, row in enumerate(rows):
            cells = row.get("tableCells", [])
            preview = " | ".join(cell_text(c).strip().replace("\n", " ")[:38] for c in cells)
            print("  r%-2d %s" % (ri, preview[:180]))


def locate(doc, table_i, row_i, col_i):
    t = tables(doc)[table_i]
    cell = t["tableRows"][row_i]["tableCells"][col_i]
    content = cell["content"]
    start = content[0]["startIndex"]
    end = content[-1]["endIndex"] - 1        # keep the cell's trailing newline
    return start, end


def _char_map(elements):
    """Flatten a list of content elements into (text, absolute index per character)."""
    chars, index_of = [], []
    for el in elements:
        if "paragraph" not in el:
            continue
        for run in el["paragraph"].get("elements", []):
            if "textRun" not in run:
                continue
            t = run["textRun"].get("content", "")
            for k, ch in enumerate(t):
                chars.append(ch)
                index_of.append(run["startIndex"] + k)
    return "".join(chars), index_of


def cmd_append(docs, doc_id, table_i, row_i, col_i, path):
    """Append paragraphs to the end of a cell, keeping the cell's existing paragraph style."""
    text = open(path, encoding="utf-8").read().rstrip("\n")
    doc = fetch(docs, doc_id)
    cell = tables(doc)[table_i]["tableRows"][row_i]["tableCells"][col_i]
    at = cell["content"][-1]["endIndex"] - 1
    body = {"requests": [{"insertText": {"location": {"index": at}, "text": "\n" + text}}]}
    docs.documents().batchUpdate(documentId=doc_id, body=body).execute()
    print("appended %d chars at %d" % (len(text), at))


def cmd_bold(docs, doc_id, table_i, row_i, col_i, needle):
    """Make one string inside a cell bold at 10pt, without touching anything else."""
    doc = fetch(docs, doc_id)
    cell = tables(doc)[table_i]["tableRows"][row_i]["tableCells"][col_i]
    text, index_of = _char_map(cell["content"])
    pos = text.find(needle)
    if pos < 0:
        sys.exit("not found: %r" % needle)
    start = index_of[pos]
    end = index_of[pos + len(needle) - 1] + 1
    body = {"requests": [{"updateTextStyle": {
        "range": {"startIndex": start, "endIndex": end},
        "textStyle": {"bold": True,
                      "weightedFontFamily": {"fontFamily": "Times New Roman"},
                      "fontSize": {"magnitude": 10, "unit": "PT"}},
        "fields": "bold,weightedFontFamily,fontSize"}}]}
    docs.documents().batchUpdate(documentId=doc_id, body=body).execute()
    print("bolded %r (%d-%d)" % (needle, start, end))


def cmd_replace_any(docs, doc_id, old, new):
    """Find the cell that holds a string and swap it there, table and row unknown."""
    doc = fetch(docs, doc_id)
    for ti, t in enumerate(tables(doc)):
        for ri, row in enumerate(t.get("tableRows", [])):
            for ci, cell in enumerate(row.get("tableCells", [])):
                text, index_of = _char_map(cell.get("content", []))
                pos = text.find(old)
                if pos < 0:
                    continue
                start = index_of[pos]
                end = index_of[pos + len(old) - 1] + 1
                body = {"requests": [
                    {"deleteContentRange": {"range": {"startIndex": start, "endIndex": end}}},
                    {"insertText": {"location": {"index": start}, "text": new}},
                ]}
                docs.documents().batchUpdate(documentId=doc_id, body=body).execute()
                print("replaced in table %d row %d: %r" % (ti, ri, old[:50]))
                return True
    print("NOT FOUND: %r" % old[:70])
    return False


def cmd_replace_body(docs, doc_id, old, new):
    """Same swap, but anywhere in the body paragraphs instead of one table cell."""
    doc = fetch(docs, doc_id)
    text, index_of = _char_map(doc.get("body", {}).get("content", []))
    pos = text.find(old)
    if pos < 0:
        sys.exit("not found in body: %r" % old)
    start = index_of[pos]
    end = index_of[pos + len(old) - 1] + 1
    body = {"requests": [
        {"deleteContentRange": {"range": {"startIndex": start, "endIndex": end}}},
        {"insertText": {"location": {"index": start}, "text": new}},
    ]}
    docs.documents().batchUpdate(documentId=doc_id, body=body).execute()
    print("replaced %r -> %r at %d" % (old, new, start))


def cmd_replace(docs, doc_id, table_i, row_i, col_i, old, new):
    """Swap one string inside a cell, keeping the paragraph style it sits in."""
    doc = fetch(docs, doc_id)
    cell = tables(doc)[table_i]["tableRows"][row_i]["tableCells"][col_i]
    # walk the cell to find absolute indices of the substring
    chars, index_of = [], []
    for el in cell.get("content", []):
        if "paragraph" not in el:
            continue
        for run in el["paragraph"].get("elements", []):
            if "textRun" not in run:
                continue
            t = run["textRun"].get("content", "")
            for k, ch in enumerate(t):
                chars.append(ch)
                index_of.append(run["startIndex"] + k)
    text = "".join(chars)
    pos = text.find(old)
    if pos < 0:
        sys.exit("not found in cell: %r" % old)
    start = index_of[pos]
    end = index_of[pos + len(old) - 1] + 1
    body = {"requests": [
        {"deleteContentRange": {"range": {"startIndex": start, "endIndex": end}}},
        {"insertText": {"location": {"index": start}, "text": new}},
    ]}
    docs.documents().batchUpdate(documentId=doc_id, body=body).execute()
    print("replaced %r -> %r at %d" % (old, new, start))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, doc_id = sys.argv[1], sys.argv[2]
    docs = service()

    if cmd == "structure":
        cmd_structure(docs, doc_id)
    elif cmd == "cell":
        doc = fetch(docs, doc_id)
        s, e = locate(doc, int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
        print(cell_text(tables(doc)[int(sys.argv[3])]["tableRows"][int(sys.argv[4])]
                        ["tableCells"][int(sys.argv[5])]))
        print("range %d-%d" % (s, e))
    elif cmd == "append-cell":
        cmd_append(docs, doc_id, int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
    elif cmd == "bold":
        cmd_bold(docs, doc_id, int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
    elif cmd == "replace-any":
        cmd_replace_any(docs, doc_id, sys.argv[3], sys.argv[4])
    elif cmd == "replace-body":
        cmd_replace_body(docs, doc_id, sys.argv[3], sys.argv[4])
    elif cmd == "replace":
        cmd_replace(docs, doc_id, int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),
                    sys.argv[6], sys.argv[7])
    elif cmd == "set-cell":
        table_i, row_i, col_i = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
        text = open(sys.argv[6], encoding="utf-8").read()
        doc = fetch(docs, doc_id)
        s, e = locate(doc, table_i, row_i, col_i)
        body = {"requests": [
            {"deleteContentRange": {"range": {"startIndex": s, "endIndex": e}}},
            {"insertText": {"location": {"index": s}, "text": text}},
        ]}
        docs.documents().batchUpdate(documentId=doc_id, body=body).execute()
        print("written %d chars into table %d r%d c%d" % (len(text), table_i, row_i, col_i))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
