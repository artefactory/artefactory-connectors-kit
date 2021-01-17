from nck.readers.mytarget_reader import MyTargetReader
from unittest import TestCase, mock
from freezegun import freeze_time
import datetime


class TestMyTargetReader(TestCase):

    kwargs = {
        "client_id": "random",
        "client_secret": "random",
        "mail": "random",
        "agency": "random",
        "agency_client_token": "random"
    }

    def mock_mytarget_reader(self, **kwargs):
        for param, value in kwargs.items():
            setattr(self, param, value)

    @freeze_time("2021-01-18")
    @mock.patch.object(MyTargetReader, "__init__", mock_mytarget_reader)
    def test_check_date_not_in_future(self):
        kwargs = {}
        reader = MyTargetReader(**kwargs)
        reader.kwargs = self.kwargs
        with self.assertRaises(ValueError):
            reader.__check_date_not_in_future(datetime.datetime(2024, 1, 1, 0, 0))
        assert self.assertTrue(reader.__check_date_not_in_future(datetime.datetime(2021, 1, 18, 0, 0)))
        assert self.assertTrue(reader.__check_date_not_in_future(datetime.datetime(2020, 1, 17, 0, 0)))

    @mock.patch.object(MyTargetReader, "__init__", mock_mytarget_reader)
    def test_check_validity_date(self):
        kwargs = {}
        reader = MyTargetReader(**kwargs)
        reader.kwargs = self.kwargs
        with self.assertRaises(ValueError):
            reader.__check_date_not_in_future(datetime.datetime(2024, 1, 1, 0, 0))
        with self.assertRaises(ValueError):
            reader.__check_date_not_in_future(datetime.datetime(2020, 13, 1, 0, 0))
        with self.assertRaises(ValueError):
            reader.__check_date_not_in_future(datetime.datetime(2020, 12, 100, 0, 0))
        assert self.assertTrue(reader.__check_date_not_in_future(datetime.datetime(2020, 3, 13, 0, 0)))

    @mock.patch.object(MyTargetReader, "__init__", mock_mytarget_reader)
    def test_check_both_start_end_valid(self):
        kwargs = {}
        reader = MyTargetReader(**kwargs)
        reader.kwargs = self.kwargs
        with self.assertRaises(ValueError):
            reader.__check_both_start_end_valid(None, datetime.datetime(2020, 1, 1, 0, 0))
        with self.assertRaises(ValueError):
            reader.__check_both_start_end_valid(datetime.datetime(2020, 1, 1, 0, 0), None)
        with self.assertRaises(ValueError):
            reader.__check_both_start_end_valid(None, None)
        assert self.assertTrue(reader.__check_both_start_end_valid(
            datetime.datetime(2020, 3, 13, 0, 0),
            datetime.datetime(2020, 3, 13, 0, 0)
        ))

    @mock.patch.object(MyTargetReader, "__init__", mock_mytarget_reader)
    def test_check_end_posterior_to_start(self):
        kwargs = {}
        reader = MyTargetReader(**kwargs)
        reader.kwargs = self.kwargs
        with self.assertRaises(ValueError):
            reader.__check_end_posterior_to_start(datetime.datetime(2020, 1, 1, 0, 0), datetime.datetime(2019, 12, 31, 0, 0))
        with self.assertRaises(ValueError):
            reader.__check_end_posterior_to_start(datetime.datetime(2020, 12, 1, 0, 0), datetime.datetime(2012, 1, 31, 0, 0))
        assert self.assertTrue(reader.__check_end_posterior_to_start(
            datetime.datetime(2020, 3, 13, 0, 0),
            datetime.datetime(2020, 3, 13, 0, 0)
        ))
        assert self.assertTrue(reader.__check_end_posterior_to_start(
            datetime.datetime(2019, 1, 13, 0, 0),
            datetime.datetime(2020, 3, 13, 0, 0)
        ))
