from flask import Flask, render_template, request, redirect, url_for, flash
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

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

def get_total_rows():
    try:
        service = get_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="A:A").execute()
        values = result.get("values", [])
        return len(values)
    except HttpError as err:
        print(err)
        return 0


def get_data(start_row=1, row_count=10):
    try:
        service = get_service()
        sheet = service.spreadsheets()

        header_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="A1:I1").execute()
        headers = header_result.get("values", [])[0]

        range_name = f"A{start_row}:I{start_row + row_count - 1}"
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
        values = result.get("values", [])

        if values:
            df = pd.DataFrame(values, columns=headers)
            df.index = df.index + start_row
            return df
        return pd.DataFrame(columns=headers)
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

def update_data(row_number, data):
    try:
        service = get_service()
        sheet = service.spreadsheets()

        current_range = f"A{row_number}:I{row_number}"
        current_row = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=current_range).execute().get('values', [[]])[0]

        for i in range(len(data)):
            if data[i] == '':
                data[i] = current_row[i] if i < len(current_row) else ''

        body = {'values': [data]}

        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID, range=current_range, valueInputOption="RAW", body=body).execute()
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

@app.route('/')
@app.route('/page/<int:page>')
def index(page=1):
    row_count = 10
    start_row = (page - 1) * row_count + 2
    data = get_data(start_row=start_row, row_count=row_count)

    if data is not None:
        total_rows = get_total_rows() - 1
        total_pages = (total_rows // row_count) + (1 if total_rows % row_count > 0 else 0)
        return render_template('index.html', data=data.to_html(classes='table table-striped', index=True), page=page, total_pages=total_pages)
    return render_template('index.html', data="No se encontraron datos.", page=page, total_pages=1)


@app.route('/add', methods=['POST'])
def add():
    data = [
        request.form['ID'],
        request.form['Nombre'],
        request.form['Email'],
        request.form['Lider'],
        request.form['FechaDesde'],
        request.form['FechaHasta'],
        request.form['Tipo'],
        request.form['Motivo'],
        request.form['Estado']
    ]
    if len(data) == 9:
        result = add_data(data)
        if result:
            flash('La información se agregó correctamente.', 'success')
        else:
            flash('No se pudo agregar la información.', 'danger')
    else:
        flash('Por favor proveer todos los valores necesarios.', 'danger')
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update():
    row_number = int(request.form['RowNumber'])
    data = [
        request.form.get('ID', ''),
        request.form.get('Nombre', ''),
        request.form.get('Email', ''),
        request.form.get('Lider', ''),
        request.form.get('FechaDesde', ''),
        request.form.get('FechaHasta', ''),
        request.form.get('Tipo', ''),
        request.form.get('Motivo', ''),
        request.form.get('Estado', '')
    ]
    result = update_data(row_number, data)
    if result:
        flash('La información se actualizó correctamente.', 'success')
    else:
        flash('No se pudo actualizar la información.', 'danger')
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete():
    row_number = request.form['RowNumber']
    if row_number.isdigit():
        result = delete_row(int(row_number))
        if result:
            flash('La fila se eliminó correctamente.', 'success')
        else:
            flash('No se pudo eliminar.', 'danger')
    else:
        flash('Por favor ingresar un número de fila válido.', 'danger')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
