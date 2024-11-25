import datetime
import pathlib
import unittest
import lab_work.main
import json
ex = pathlib.Path(__file__).parent.joinpath("example.json")

class MyTestCase(unittest.TestCase):
    
    def test_get_issue_item_to_time_1(self):
        f=ex.open()
        data = json.load(f)
        f.close()
        field = 'status'
        toString = 'Closed'
        res = lab_work.main.get_issue_item_to_time(data,field,toString)
        base = datetime.datetime.strptime('2021-03-11T08:27:32.763+0000', '%Y-%m-%dT%H:%M:%S.%f%z')
        self.assertEqual(res,[base])
    
    def test_get_issue_item_to_time_2(self):
        f = ex.open()
        data = json.load(f)
        f.close()
        field = 'status'
        to = '6'
        res = lab_work.main.get_issue_item_to_time(data, field, to)
        base = datetime.datetime.strptime('2022-06-22T08:27:32.763+0000', '%Y-%m-%dT%H:%M:%S.%f%z')
        self.assertEqual(res, [base])
        
    
    def test_get_issue_item_to_time_3(self):
        f = ex.open()
        data = json.load(f)
        f.close()
        field = 'status'
        to = '777'
        res = lab_work.main.get_issue_item_to_time(data, field, to)
        self.assertEqual(res, [])
        
    def test_summ_elements_1(self):
        list1 = [0,1,2,3,4]
        res = lab_work.main.summ_elements(list1)
        self.assertEqual(res, [0,1,3,6,10])
    
    
    def test_summ_elements_2(self):
        list1 = []
        res = lab_work.main.summ_elements(list1)
        self.assertEqual(res, [])