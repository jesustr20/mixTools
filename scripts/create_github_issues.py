#!/usr/bin/env python3
"""
Crea issues de GitHub a partir de docs/issues/*.md, usando el `gh` CLI.

Por qué Python y no bash puro: parsear frontmatter + actualizar el body de
los epics con checklists de sub-issues es mucho más confiable con manejo
de texto real que con sed/awk. Cero dependencias externas (solo stdlib) para
que corra en cualquier máquina sin `pip install` previo.

Requisitos: `gh` instalado y autenticado (`gh auth status`).
Uso:
    python3 scripts/create_github_issues.py --repo owner/nombre-repo
    python3 scripts/create_github_issues.py --repo owner/nombre-repo --dry-run
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ISSUES_DIR = Path(__file__).resolve().parents[1] / "docs" / "issues"


def parse_issue_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: falta el frontmatter (---)")
    _, fm_block, body = text.split("---", 2)

    meta = {}
    for line in fm_block.strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()

    meta["labels"] = [l.strip() for l in meta.get("labels", "").split(",") if l.strip()]
    meta["body"] = body.strip() + "\n"
    meta["_file"] = path.name
    return meta


def run(cmd: list[str], dry_run: bool, capture: bool = True) -> str:
    if dry_run:
        print(f"  [dry-run] $ {' '.join(cmd)}")
        return ""
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Falló: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def check_prereqs():
    if subprocess.run(["which", "gh"], capture_output=True).returncode != 0:
        sys.exit("ERROR: falta instalar GitHub CLI (gh). Ver https://cli.github.com/")
    auth = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    if auth.returncode != 0:
        sys.exit("ERROR: gh no está autenticado. Corré `gh auth login` primero.")


def find_existing_issue(repo: str, title: str) -> str | None:
    """Busca por título exacto para no duplicar en reruns."""
    out = subprocess.run(
        ["gh", "issue", "list", "--repo", repo, "--state", "all",
         "--search", f'"{title}" in:title', "--json", "number,title", "--limit", "20"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        return None
    try:
        items = json.loads(out.stdout)
    except json.JSONDecodeError:
        return None
    for item in items:
        if item["title"] == title:
            return str(item["number"])
    return None


def ensure_milestone(repo: str, title: str, dry_run: bool):
    if not title:
        return
    if dry_run:
        print(f"  [dry-run] confirmaría/crearía milestone '{title}'")
        return
    existing = subprocess.run(
        ["gh", "api", f"repos/{repo}/milestones", "--jq", f'.[] | select(.title=="{title}") | .number'],
        capture_output=True, text=True,
    )
    if existing.stdout.strip():
        return
    print(f"  Creando milestone '{title}'…")
    run(["gh", "api", f"repos/{repo}/milestones", "-f", f"title={title}"], dry_run, capture=False)


def append_subissue_link(repo: str, epic_number: str, child_number: str, child_title: str, dry_run: bool):
    if dry_run:
        print(f"  [dry-run] añadir #{child_number} al checklist del epic #{epic_number}")
        return
    body = run(["gh", "issue", "view", epic_number, "--repo", repo, "--json", "body", "-q", ".body"], dry_run)
    marker = "## Sub-issues"
    line = f"- [ ] #{child_number} {child_title}"
    if marker not in body:
        body = body.rstrip() + f"\n\n{marker}\n{line}\n"
    elif line not in body:
        body = body.rstrip() + f"\n{line}\n"
    else:
        return  # ya estaba
    tmp = Path("/tmp/_epic_body.md")
    tmp.write_text(body, encoding="utf-8")
    run(["gh", "issue", "edit", epic_number, "--repo", repo, "--body-file", str(tmp)], dry_run, capture=False)


def create_issue(repo: str, meta: dict, dry_run: bool) -> str:
    title = meta["title"]
    existing = None if dry_run else find_existing_issue(repo, title)
    if existing:
        print(f"  ya existe (#{existing}), se omite: {title}")
        return existing

    body_file = Path(f"/tmp/_issue_body_{meta.get('slug','x')}.md")
    body_file.write_text(meta["body"], encoding="utf-8")

    cmd = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body-file", str(body_file)]
    for label in meta["labels"]:
        cmd += ["--label", label]
    if meta.get("milestone"):
        cmd += ["--milestone", meta["milestone"]]

    print(f"  creando: {title}")
    out = run(cmd, dry_run)
    if dry_run:
        return "0"
    number = out.rstrip("/").split("/")[-1]
    print(f"    -> #{number}")
    return number


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="owner/nombre-repo")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dry_run:
        check_prereqs()

    files = sorted(ISSUES_DIR.glob("*.md"))
    if not files:
        sys.exit(f"No hay archivos en {ISSUES_DIR}")

    issues = [parse_issue_file(f) for f in files]
    epics = [i for i in issues if not i.get("epic")]
    children = [i for i in issues if i.get("epic")]

    milestones = {i.get("milestone") for i in issues if i.get("milestone")}
    for ms in milestones:
        ensure_milestone(args.repo, ms, args.dry_run)

    print(f"\n== Creando {len(epics)} epics ==")
    slug_to_number = {}
    for epic in epics:
        number = create_issue(args.repo, epic, args.dry_run)
        slug_to_number[epic["slug"]] = number

    print(f"\n== Creando {len(children)} stories/tech-tasks/spikes ==")
    for child in children:
        epic_slug = child["epic"]
        epic_number = slug_to_number.get(epic_slug)
        if epic_number:
            child["body"] += f"\nParte de #{epic_number}\n"
        number = create_issue(args.repo, child, args.dry_run)
        if epic_number and number != "0":
            append_subissue_link(args.repo, epic_number, number, child["title"], args.dry_run)

    print("\nListo.")


if __name__ == "__main__":
    main()
