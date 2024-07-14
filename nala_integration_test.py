import unittest
from nala import get_data, add_data, update_data, delete_row

class TestGoogleSheetAPIIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_row = ['999', 'Test User', 'test@example.com', 'Test Leader', '2023-01-01', '2023-01-10', 'Vacaciones', 'Test Motivo', 'Pendiente']
        cls.updated_row = ['999', 'Updated User', 'updated@example.com', 'Updated Leader', '2023-01-01', '2023-01-10', 'Vacaciones', 'Updated Motivo', 'Aprobado']
        cls.row_number = None

    def test_1_get_data(self):
        data = get_data()
        self.assertIsNotNone(data)
        self.assertIsInstance(data, list)

    def test_add_data(self):
        result = add_data(self.test_row)
        self.assertIsNotNone(result)
        data = get_data()
        self.assertIn(self.test_row, data)
        self.__class__.row_number = len(data)

    def test_update_data(self):
        result = update_data(self.row_number, data=self.updated_row)
        self.assertIsNotNone(result)
        data = get_data()
        self.assertIn(self.updated_row, data)

    def test_delete_row(self):
        self.assertIsNotNone(self.row_number, "Row number should be set by test_1_add_data")
        result = delete_row(self.row_number)
        self.assertIsNotNone(result)
        data = get_data()
        self.assertNotIn(self.updated_row, data)

if __name__ == "__main__":
    unittest.main()
