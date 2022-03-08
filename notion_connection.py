import os
from pprint import pprint

import pandas as pd
from notion_client import Client


class NotionConnection:
    def __init__(self) -> None:
        NOTION_TOKEN = os.getenv("NOTION_SECRET")
        assert len(NOTION_TOKEN) > 0

        self.notion = Client(auth=NOTION_TOKEN)

    def add(self, title, time_str, db_title="test-db"):

        db_id = self.notion.search(query=db_title).get("results")[0]["id"]
        db_parent = dict(type="database_id", database_id=db_id)

        new_page = {
            "name": {"title": [{"text": {"content": title}}]},
            "date": {"type": "date", "date": {"start": time_str}},
        }

        self.notion.pages.create(parent=db_parent, properties=new_page)

    def get_items_from_db(self, db_title="test-db"):
        db_id = self.notion.search(query=db_title).get("results")[0]["id"]
        response = self.notion.databases.query(database_id=db_id)

        l = []
        for item in response["results"]:
            try:
                title = item["properties"]["name"]["title"][0]["plain_text"]
                time = item["properties"]["date"]["date"]["start"]
                l.append((title, time[:19]))  # truncate, no timezone
            except Exception as e:
                print(e)
                pprint(item)

        return l

    def get_table(self, db_title="test-db"):
        items = self.get_items_from_db(db_title=db_title)
        return [f"{title}\t{time}" for title, time in items]

    def get_table_groupby_date(self, db_title="test-db"):
        items = self.get_items_from_db(db_title=db_title)

        l = []
        for title, time in items:
            d = pd.Timestamp(time).date()
            l.append((title, time, d))

        df = pd.DataFrame(l, columns=["title", "time", "date"])

        ll = []
        for _, dz in df.groupby("date"):
            ll.append(list(dz.itertuples()))

        return ll[::-1]
