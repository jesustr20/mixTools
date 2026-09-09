#!/usr/bin/env python3
"""
Sincroniza labels de GitHub desde docs/labels.yaml.
Parser de YAML manual (solo entiende el subset que usa labels.yaml) para no
depender de PyYAML en la máquina de quien lo corra.
"""
import argparse
import subprocess
import sys
from pathlib import Path

LABELS_FILE = Path(__file__).resolve().parents[1] / "docs" / "labels.yaml"


def parse_labels_yaml(path: Path) -> list[dict]:
    labels = []
    current = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- name:"):
            if current:
                labels.append(current)
            current = {"name": line.split(":", 1)[1].strip().strip('"')}
        elif line.startswith("color:") and current is not None:
            current["color"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("description:") and current is not None:
            current["description"] = line.split(":", 1)[1].strip().strip('"')
    if current:
        labels.append(current)
    return labels


def existing_labels(repo: str) -> dict:
    out = subprocess.run(
        ["gh", "label", "list", "--repo", repo, "--json", "name,color,description", "--limit", "200"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        return {}
    import json
    return {l["name"]: l for l in json.loads(out.stdout)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    labels = parse_labels_yaml(LABELS_FILE)
    current = {} if args.dry_run else existing_labels(args.repo)

    for label in labels:
        name, color, desc = label["name"], label.get("color", "ededed"), label.get("description", "")
        if name in current:
            if current[name]["color"] != color or current[name].get("description", "") != desc:
                print(f"  actualizando: {name}")
                cmd = ["gh", "label", "edit", name, "--repo", args.repo, "--color", color, "--description", desc]
            else:
                continue
        else:
            print(f"  creando: {name}")
            cmd = ["gh", "label", "create", name, "--repo", args.repo, "--color", color, "--description", desc, "--force"]
        if args.dry_run:
            print(f"    [dry-run] $ {' '.join(cmd)}")
        else:
            subprocess.run(cmd, check=True)

    print("Labels sincronizados.")


if __name__ == "__main__":
    main()
