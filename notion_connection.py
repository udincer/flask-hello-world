import os

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
