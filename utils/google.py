import gspread
import json


class GoogleSheest():

    def __init__(self) -> None:
        with open("config.json", "rb") as file:
            data = json.load(file)
            self.api_id = data["api_id"]
            self.api_hash = data["api_hash"]
            self.phone = data["phone"]
            self.teachers = data["teachers_list"]

    def __init__(self) -> None:
        with open("config.json", "rb") as file:
            data = json.load(file)
            self.gs_filename = data["gs_filename"]
            self.gs_name = data["gs_name"]
        self.gc = gspread.service_account(self.gs_filename)
        self.sh = self.gc.open(self.gs_name)

    def collect_data(self):
        worksheet = self.sh.get_worksheet(0)
        result = []
        cells = worksheet.get_values()
        for cell in cells:
            if cell[6].lower() == "да":
                result.append(cell)
        return result
