import re
import subprocess
import tempfile
from pathlib import Path

def normalize_obsidian_embeds(md_text: str) -> str:
    # Convert Obsidian image embeds ![[path|...]] -> ![](path)
    def repl(m: re.Match) -> str:
        inner = m.group(1).strip()
        path = inner.split("|", 1)[0].strip()  # ignore size/alias after |
        return f"![]({path})"

    md_text = re.sub(r"!\[\[([^\]]+?)\]\]", repl, md_text)

    # Optional: convert Obsidian wikilinks [[Page]] -> Page (plain text)
    md_text = re.sub(r"\[\[([^\]]+?)\]\]", lambda m: m.group(1).split("|", 1)[0], md_text)

    return md_text

def md_to_docx(md_path: str, out_path: str):
    md_file = Path(md_path).resolve()
    out_file = Path(out_path).resolve()
    base_dir = md_file.parent

    raw = md_file.read_text(encoding="utf-8")
    fixed = normalize_obsidian_embeds(raw)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_md = Path(tmp) / md_file.name
        tmp_md.write_text(fixed, encoding="utf-8")

        # Resource paths where images can be found:
        # - md folder itself
        # - common subfolders (add your own if needed)
        resource_dirs = [
            str(base_dir),
            str(base_dir / "assets"),
            str(base_dir / "attachments"),
            str(base_dir / "Images"),
            str(base_dir / "images"),
        ]

        # Pandoc on Windows expects ';' as separator, on Unix ':'
        sep = ";" if subprocess.os.name == "nt" else ":"
        resource_path = sep.join([p for p in resource_dirs if Path(p).exists()])

        cmd = [
            "pandoc",
            str(tmp_md),
            "-o",
            str(out_file),
            "--resource-path",
            resource_path,
        ]

        subprocess.run(cmd, check=True)

if __name__ == "__main__":
    # Example:
    # python md_to_docx.py "C:\notes\my.md" "C:\notes\my.docx"
    import sys
    if len(sys.argv) != 3:
        print("Usage: python md_to_docx.py <input.md> <output.docx>")
        raise SystemExit(1)

    md_to_docx(sys.argv[1], sys.argv[2])
    print("Done.")