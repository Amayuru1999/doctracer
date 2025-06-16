import re
from deepdiff import DeepDiff
from doctracer.models.gazette import GazetteData
from typing import List, Dict

class GazetteDiffProcessor:
    @staticmethod
    def diff(old_json: str, new_json: str) -> List[Dict]:
        old = GazetteData.parse_raw(old_json).dict()
        new = GazetteData.parse_raw(new_json).dict()
        dd = DeepDiff(old, new, ignore_order=True).to_dict()

        changes = []
        for op, items in dd.items():
            for path, detail in items.items():
                # e.g. path = "root['ministers'][0]['departments'][+]…"
                m = re.search(r"ministers'\]\[(\d+)\]\['(\w+)'\]\[([+\-])\]", path)
                if not m: continue
                idx, field, flag = m.groups()
                minister = new["ministers"][int(idx)]["name"]
                value = detail.get("value") or detail
                changes.append({
                    "type": "ADD" if flag=="+" else "REMOVE",
                    "minister": minister,
                    "field": field,
                    "value": value,
                    "gazette_id": new["gazette_id"],
                    "date": new["published_date"]
                })
        return changes
