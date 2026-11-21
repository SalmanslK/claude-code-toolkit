"""List the FSD Doc's comment threads touched since a date.

The Drive connector's read_file_content(includeComments=true) result is too
large for the tool window and lands on disk as JSON:
    {commentThreads: [{commentId, status, headPost, replies}], fileContent: "..."}

Usage:
    python fsd_comments.py SAVED_JSON --since 2026-09-22T13:00 [--out DIR]

Prints every thread whose head post or any reply was modified at or after
--since, oldest first, with all replies. With --out, also writes
fsd-comments-all.txt (every thread) and fsd-live-doc.txt (the Doc's own text,
whose tables are more reliable than pdftotext's) into DIR.

Threads carry no anchor to their place in the text: tie each one to a section
by its own wording.
"""
import argparse
import json
import os
import sys


def last_touched(thread: dict) -> str:
    stamps = [thread["headPost"].get("modifiedTime", "")]
    stamps += [reply.get("modifiedTime", "") for reply in thread.get("replies", [])]
    return max(stamps)


def render(thread: dict) -> str:
    head = thread["headPost"]
    lines = [f"### {thread['commentId']} [{thread.get('status', '?')}] "
             f"{head.get('authorName', '?')} {head.get('modifiedTime', '')[:16]}",
             f"Q: {head.get('content', '')}"]
    for reply in thread.get("replies", []):
        lines.append(f"  -> {reply.get('authorName', '?')} {reply.get('modifiedTime', '')[:16]}: "
                     f"{reply.get('content', '')}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("saved_json")
    parser.add_argument("--since", required=True, help="ISO timestamp, e.g. 2026-09-22T13:00")
    parser.add_argument("--out")
    args = parser.parse_args()

    data = json.load(open(args.saved_json, encoding="utf-8"))
    threads = data["commentThreads"]
    open_count = sum(1 for t in threads if t.get("status") == "OPEN")
    recent = sorted((t for t in threads if last_touched(t) >= args.since), key=last_touched)

    sys.stdout.reconfigure(encoding="utf-8")
    print(f"{len(threads)} threads, {open_count} open; {len(recent)} touched since {args.since}\n")
    for thread in recent:
        print(render(thread) + "\n")

    if args.out:
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "fsd-comments-all.txt"), "w", encoding="utf-8") as handle:
            handle.write("\n\n".join(render(t) for t in threads))
        with open(os.path.join(args.out, "fsd-live-doc.txt"), "w", encoding="utf-8") as handle:
            handle.write(data.get("fileContent", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
