import gspread
from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = "1iMTnYZxLKW1In1HyWHKEw7fC0j6qSP1zhN85CA_cKDM"

sheet = client.open_by_key(sheet_id)


async def check_register(user_id: int) -> bool:
    """
    Checking user id in A1 column (user_id)
    """
    user_ids = sheet.sheet1.col_values(4)
    if str(user_id) in user_ids:
        return True
    return False


async def add_new_user(user_data) -> None:
    try:

        sheet.sheet1.append_row(
            [
                user_data.get("weight"),
                user_data.get("height"),
                user_data.get("age"),
                user_data.get("user_id"),
                user_data.get("chat_id"),
                user_data.get("registered_date"),
            ],
            "user",
        )
    except Exception as sheetEX:
        print(sheetEX)
    return True


# add_new_user("1337", "1337")
