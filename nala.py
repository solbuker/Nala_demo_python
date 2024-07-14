import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys
import pandas as pd

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = "1JfQ4g3o-4PuYxingww96VA2NlzUmyM1RnRuHij7YeYM"
RANGE_NAME = "A:I"
SHEET_ID = 1335689066

def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)

def get_data():
    try:
        service = get_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get("values", [])
        if values:
            df = pd.DataFrame(values[1:], columns=values[0])
            return df
        return None
    except HttpError as err:
        print(err)
        return None

def add_data(data):
    try:
        service = get_service()
        body = {'values': [data]}
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME, valueInputOption="RAW", body=body).execute()
        return result
    except HttpError as err:
        print(err)
        return None

def update_data(row_number, data=None, column=None, value=None):
    try:
        service = get_service()
        if data:
            range_to_update = f"A{row_number}:I{row_number}"
            body = {'values': [data]}
        else:
            range_to_update = f"{column}{row_number}"
            body = {'values': [[value]]}
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=range_to_update, valueInputOption="RAW", body=body).execute()
        return result
    except HttpError as err:
        print(err)
        return None

def delete_row(row_number):
    try:
        service = get_service()
        requests = [{
            'deleteDimension': {
                'range': {
                    'sheetId': SHEET_ID,
                    'dimension': 'ROWS',
                    'startIndex': row_number - 1,
                    'endIndex': row_number
                }
            }
        }]
        body = {'requests': requests}
        result = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        return result
    except HttpError as err:
        print(err)
        return None

def data_entry():
    data = [
        input("Enter ID: "),
        input("Enter Nombre: "),
        input("Enter Email: "),
        input("Enter Líder: "),
        input("Enter Fecha desde (YYYY-MM-DD): "),
        input("Enter Fecha hasta (YYYY-MM-DD): "),
        input("Enter Tipo: "),
        input("Enter Motivo (opcional): ")
    ]
    while True:
        estado = input("Enter Estado (Aprobado/Rechazado/Pendiente): ").strip()
        if estado in ["Aprobado", "Rechazado", "Pendiente"]:
            data.append(estado)
            break
        else:
            print("Estado inválido.")
    return data

def handle_read():
    data = get_data()
    if data is not None:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.colheader_justify', 'center')
        print(data)
    else:
        print("No se encontraron datos.")

def handle_add():
    data = data_entry()
    if len(data) == 9:
        result = add_data(data)
        if result:
            print("La información se agregó correctamente.")
        else:
            print("No se pudo agregar la información.")
    else:
        print("Por favor proveer todos los valores necesarios.")

def handle_update():
    row_number = input("Ingrese la fila que desea actualizar: ")
    if row_number.isdigit():
        update_type = input("Desea actualizar toda la fila o un valor específico? (fila/valor): ").strip().lower()
        if update_type == "fila":
            data = data_entry()
            if len(data) == 9:
                result = update_data(int(row_number), data=data)
                if result:
                    print("La información se actualizó correctamente.")
                else:
                    print("No se pudo actualizar la información.")
            else:
                print("Por favor proveer todos los valores necesarios.")
        elif update_type == "valor":
            column = input("Ingrese la columna (A-I): ").strip().upper()
            value = input(f"Ingrese el nuevo valor para la columna {column}: ")
            if column in "ABCDEFGHI":
                result = update_data(int(row_number), column=column, value=value)
                if result:
                    print("La información se actualizó correctamente.")
                else:
                    print("No se pudo actualizar la información.")
            else:
                print("Por favor ingresar una columna válida (A-I).")
    else:
        print("Por favor ingresar un número de fila válido.")

def handle_delete():
    row_number = input("Ingrese la fila a eliminar: ")
    if row_number.isdigit():
        result = delete_row(int(row_number))
        if result:
            print("La fila se eliminó correctamente.")
        else:
            print("No se pudo eliminar.")
    else:
        print("Por favor ingresar un número de fila válido.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "leer_datos":
            handle_read()
        elif command == "agregar_datos":
            handle_add()
        elif command == "actualizar_datos":
            handle_update()
        elif command == "eliminar_datos":
            handle_delete()
        else:
            print("Comando no reconocido. Uso: python gsheet_api.py [leer_datos|agregar_datos|actualizar_datos|eliminar_datos]")
