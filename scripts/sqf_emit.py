# Emits trailers or a summary from the newest SquirrelFocus journal entry.
import sys
import os
import glob
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_PATH = os.path.join(ROOT, '.squirrelfocus', 'config.yaml')


def newest_md(jdir):
    files = [
        f
        for f in glob.glob(
            os.path.join(ROOT, jdir, '**', '*.md'), recursive=True
        )
    ]
    return max(files, key=os.path.getmtime) if files else None


def split_frontmatter(text):
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            _, fm, body = parts[0], parts[1], parts[2]
            try:
                import yaml as _yaml
                return _yaml.safe_load(fm), body
            except Exception:
                return {}, text
    return {}, text


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'trailers'
    if not os.path.exists(CFG_PATH):
        print('', end='')
        return
    cfg = yaml.safe_load(open(CFG_PATH, 'r', encoding='utf-8'))
    jdir = cfg.get('journals_dir', 'journal_logs')
    keys = cfg.get('trailer_keys', [])
    tmpl = cfg.get('summary_format', '')
    path = newest_md(jdir)
    if not path:
        print('', end='')
        return
    text = open(path, 'r', encoding='utf-8').read()
    fm, _ = split_frontmatter(text)
    trailers = (fm or {}).get('trailers', {})
    if mode == 'trailers':
        lines = [
            f"{k}: {trailers.get(k, '').strip()}"
            for k in keys
            if trailers.get(k)
        ]
        print('\n'.join(lines))
    elif mode == 'summary':
        msg = tmpl
        for k in keys:
            msg = msg.replace('{{' + k + '}}', str(trailers.get(k, '')))
        print(msg)
    else:
        print('', end='')


if __name__ == '__main__':
    main()
