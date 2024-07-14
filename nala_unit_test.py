import unittest
from unittest.mock import patch, MagicMock
import nala

class TestGoogleSheetAPI(unittest.TestCase):

    @patch('nala.build')
    def test_get_data(self, mock_build):
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.values.return_value.get.return_value.execute.return_value = {
            'values': [
                ['ID', 'Nombre', 'Email', 'Líder', 'Fecha desde', 'Fecha hasta', 'Tipo', 'Motivo', 'Estado'],
                ['1', 'John Doe', 'john@example.com', 'Líder 1', '2023-01-01', '2023-01-10', 'Vacaciones', 'Motivo 1', 'Aprobado']
            ]
        }

        data = nala.get_data()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0][0], 'ID')
        self.assertEqual(data[1][1], 'John Doe')

    @patch('nala.build')
    def test_add_data(self, mock_build):
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.values.return_value.append.return_value.execute.return_value = {'updates': {'updatedRows': 1}}

        result = nala.add_data(['2', 'Jane Doe', 'jane@example.com', 'Líder 2', '2023-02-01', '2023-02-10', 'Vacaciones', 'Motivo 2', 'Pendiente'])

        self.assertIn('updatedRows', result['updates'])
        self.assertEqual(result['updates']['updatedRows'], 1)

    @patch('nala.build')
    def test_update_data(self, mock_build):
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.values.return_value.update.return_value.execute.return_value = {'updatedCells': 9}

        result = nala.update_data(2, data=['2', 'Jane Doe', 'jane@example.com', 'Líder 2', '2023-02-01', '2023-02-10', 'Vacaciones', 'Motivo 2', 'Aprobado'])

        self.assertIn('updatedCells', result)
        self.assertEqual(result['updatedCells'], 9)

    @patch('nala.build')
    def test_delete_row(self, mock_build):
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.batchUpdate.return_value.execute.return_value = {'replies': [{}]}

        result = nala.delete_row(2)

        self.assertIn('replies', result)
        self.assertEqual(len(result['replies']), 1)

if __name__ == "__main__":
    unittest.main()
