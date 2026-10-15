"""links.csv를 읽어서 slug마다 리다이렉트 페이지를 만든다. 결과는 _site/ 폴더."""
import csv, html, json, os, re, shutil, sys

HOME = "https://www.buildingrich.co.kr/"
OUT = "_site"

PAGE = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0;url={href}">
<link rel="canonical" href="{href}">
<title>빌딩앤리치</title>
<script>location.replace({js});</script>
</head><body><a href="{href}">빌딩앤리치로 이동</a></body></html>
"""

def page(url):
    return PAGE.format(href=html.escape(url, quote=True), js=json.dumps(url))

def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    seen, errors = set(), []
    with open("links.csv", encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            slug = (row.get("slug") or "").strip().strip("/")
            url = (row.get("url") or "").strip()
            if not slug and not url:
                continue
            if not re.fullmatch(r"[A-Za-z0-9_-]+", slug):
                errors.append(f"{i}행: slug '{slug}'는 영문·숫자·-·_만 가능")
                continue
            if slug.lower() in seen:
                errors.append(f"{i}행: slug '{slug}' 중복")
                continue
            if not url.startswith(("http://", "https://")):
                errors.append(f"{i}행: url이 http로 시작하지 않음")
                continue
            seen.add(slug.lower())
            os.makedirs(os.path.join(OUT, slug))
            with open(os.path.join(OUT, slug, "index.html"), "w", encoding="utf-8") as o:
                o.write(page(url))
    # 루트와 없는 주소는 홈페이지로
    for name in ("index.html", "404.html"):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as o:
            o.write(page(HOME))
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"{len(seen)}개 링크 생성")

if __name__ == "__main__":
    main()
