import os

import requests
import pandas as pd


class TogglConnection:
    def __init__(self) -> None:
        TOGGL_TOKEN = os.getenv("TOGGL_TOKEN")
        if TOGGL_TOKEN is not None and len(TOGGL_TOKEN) > 0:
            self.auth = (TOGGL_TOKEN, "api_token")
            self.WORKSPACE_ID = "6201012"
            self.project_id_mapping = self.get_project_id_mapping()
        else:
            raise ValueError("TOGGL_TOKEN environment variable not set")

    def get_project_id_mapping(self):
        workspace_id = self.WORKSPACE_ID
        url = f"https://api.track.toggl.com/api/v8/workspaces/{workspace_id}/projects"

        r = requests.get(url, auth=self.auth)
        project_id_mapping = {p["name"]: p["id"] for p in r.json()}
        return project_id_mapping

    def start_timer(self, description, project_id):
        url = "https://api.track.toggl.com/api/v8/time_entries/start"

        data = {
            "time_entry": dict(
                description=description,
                pid=self.project_id_mapping.get(project_id, project_id),
                created_with="nfc_app",
            )
        }

        r = requests.post(url, json=data, auth=self.auth)
        return r.status_code

    def get_current(self):
        url = "https://api.track.toggl.com/api/v8/time_entries/current"
        r = requests.get(url, auth=self.auth)
        data = r.json()["data"]

        if data is not None:
            start_time = (
                pd.Timestamp(data["start"]).tz_convert(tz="America/Los_Angeles").isoformat()
            )
            data["start_time_LA"] = start_time
            
        return data

    def get_current_id(self):
        data = self.get_current()
        if data is None:
            return None
        else:
            return data["id"]

    def stop_current_timer(self):
        current_id = self.get_current_id()
        if current_id is not None:
            url = f"https://api.track.toggl.com/api/v8/time_entries/{current_id}/stop"
            r = requests.put(url, auth=self.auth)
            return r.status_code
