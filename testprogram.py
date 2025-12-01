import unittest
import json
import os
import xmlrunner
from app import app, load_data, save_data, PawnItem

class TestPawnshopApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.test_db_file = "test_pawnshop_data.json"
        app.config['DB_FILE'] = self.test_db_file
        
        import app as app_module
        self.original_db_file = app_module.DB_FILE
        app_module.DB_FILE = self.test_db_file

        test_items = [
            PawnItem(1, "Золоте кільце", "Іваненко Іван", 2000, "in_storage"),
            PawnItem(2, "Ноутбук Lenovo", "Петренко Петро", 5000, "in_storage")
        ]
        with open(self.test_db_file, "w", encoding="utf-8") as f:
            json.dump([i.to_dict() for i in test_items], f, ensure_ascii=False, indent=4)

    def tearDown(self):

        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)
        import app as app_module
        app_module.DB_FILE = self.original_db_file

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'text/html', response.content_type.encode())

    def test_add_item(self):
        response = self.app.post('/add', data={
            'title': 'Телефон iPhone',
            'owner': 'Сидоренко Сидір',
            'loan_amount': '3000'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        items = load_data()
        self.assertEqual(len(items), 3)
        self.assertEqual(items[2].title, 'Телефон iPhone')
        self.assertEqual(items[2].owner, 'Сидоренко Сидір')
        self.assertEqual(items[2].loan_amount, 3000.0)

    def test_delete_item(self):
        response = self.app.get('/delete/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        items = load_data()
        self.assertEqual(len(items), 1)
        self.assertNotIn(1, [i.item_id for i in items])

    def test_update_status(self):
        response = self.app.post('/update/1', data={
            'status': 'redeemed'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        items = load_data()
        item = next((i for i in items if i.item_id == 1), None)
        self.assertIsNotNone(item)
        self.assertEqual(item.status, 'redeemed')

    def test_load_data(self):
        items = load_data()
        self.assertEqual(len(items), 2)
        self.assertIsInstance(items[0], PawnItem)
        self.assertEqual(items[0].title, "Золоте кільце")

    def test_save_data(self):
        new_items = [
            PawnItem(1, "Тестовий предмет", "Тестовий власник", 1000, "in_storage")
        ]
        save_data(new_items)

        items = load_data()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Тестовий предмет")

    def test_pawnitem_to_dict(self):
        item = PawnItem(1, "Тест", "Власник", 500, "in_storage")
        item_dict = item.to_dict()

        self.assertEqual(item_dict['item_id'], 1)
        self.assertEqual(item_dict['title'], "Тест")
        self.assertEqual(item_dict['owner'], "Власник")
        self.assertEqual(item_dict['loan_amount'], 500)
        self.assertEqual(item_dict['status'], "in_storage")


if __name__ == "__main__":
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    unittest.main(testRunner=runner)
