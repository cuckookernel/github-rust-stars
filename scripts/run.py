#!/bin/env python

import sys
import json
import requests
import time
from pathlib import Path
from requests import Response
DATA_DIR = 'data'

def main(): 
    subcommand = sys.argv[1]
    lang = sys.argv[2]
    if subcommand == 'refresh-md':         
        generate_md(lang=lang)

    elif subcommand == 'download-data':
        download_all_metadata(lang=lang)


def generate_md(lang: str):
    # %%
    with Path(f"{DATA_DIR}/all-{lang}-projs.1020.json").open("rt") as f_in:
         items = json.load(f_in)

    print(f"items has {len(items)}")

    items = sorted(items, key=lambda it: it['stargazers_count'], reverse=True)
    # %%
    out_path = Path(f"{DATA_DIR}/all-rust-projs.md")
    with out_path.open("wt") as f_out:
        for i, item in enumerate(items):
            full_name = item["full_name"]
            description = item["description"]
            # fork = item["fork"]
            # updated = item["updated_at"][:10]
            topics = item["topics"]
            url = item['svn_url']
            archived = item['archived']
            if archived:
                url_str = f"{url} (ARCHIVED)"
            else:
                url_str = url
            topics_str = ' '.join(f"#{topic}" for topic in topics)

            stars = item["stargazers_count"]
            # if 'ai' in topics or 'machine-learning' in topics or 'ml' in topics or 'learning' in topics_str :
            if True:

                print(f"### {i}. {full_name}  ({stars} ⭐)\n"
                      f"\n{topics_str}\n"                      
                      f"\n{description}\n"
                      f"\n{url_str}\n\n",
                      file=f_out)
        print(f"wrote {len(items)} to {out_path.absolute()}")
    # %%

def download_all_metadata(lang: str):
    """Download all public github repos' metadata for the given language""" 
    # %%
    # From: https://stackoverflow.com/questions/16417162/github-api-how-to-get-all-repositories-written-in-a-given-language
    # curl -H 'Accept: application/vnd.github.preview.text-match+json' \
    #   https://api.github.com/search/repositories?q=language:go&order=desc
    # %%

    all_items = []
    url_tmpl = 'https://api.github.com/search/repositories?q=language:{lang}&order=desc&page={page_num}'

    # %%
    p_start = 11
    page_num = p_start
    for page_num in range(p_start, 1000):
        url = url_tmpl.format(page_num=page_num, lang=lang)
        resp = requests.get(url,
                            headers={'Accept': 'application/vnd.github.preview.text-match+json'})

        if resp.status_code != 200:
            break

        resp_json = resp.json()
        data = resp_json['items']
        all_items.extend(data)
        print(f"url: {url} got {len(data)} items")
        time.sleep(3.0)

    out_path = f"{DATA_DIR}/all-rust-projs.p{p_start}-{page_num}.json"
    with  Path(out_path).open("wt") as f_out:
        json.dump(all_items, f_out, indent=4)
    # %%


def get_next_url(resp: Response) -> str:
    part0: str = resp.headers['Link'].split(';')[0]
    return part0.strip('<>')
    # %%


if __name__ == '__main__':
    main()

