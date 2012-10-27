import mock

from mopidy.backends import base
from mopidy.core import Core
from mopidy.models import Playlist, Track

from tests import unittest


class CoreLibraryTest(unittest.TestCase):
    def setUp(self):
        self.backend1 = mock.Mock()
        self.backend1.uri_schemes.get.return_value = ['dummy1']
        self.library1 = mock.Mock(spec=base.BaseLibraryProvider)
        self.backend1.library = self.library1

        self.backend2 = mock.Mock()
        self.backend2.uri_schemes.get.return_value = ['dummy2']
        self.library2 = mock.Mock(spec=base.BaseLibraryProvider)
        self.backend2.library = self.library2

        self.core = Core(audio=None, backends=[self.backend1, self.backend2])

    def test_lookup_selects_dummy1_backend(self):
        self.core.library.lookup('dummy1:a')

        self.library1.lookup.assert_called_once_with('dummy1:a')
        self.assertFalse(self.library2.lookup.called)

    def test_lookup_selects_dummy2_backend(self):
        self.core.library.lookup('dummy2:a')

        self.assertFalse(self.library1.lookup.called)
        self.library2.lookup.assert_called_once_with('dummy2:a')

    def test_refresh_with_uri_selects_dummy1_backend(self):
        self.core.library.refresh('dummy1:a')

        self.library1.refresh.assert_called_once_with('dummy1:a')
        self.assertFalse(self.library2.refresh.called)

    def test_refresh_with_uri_selects_dummy2_backend(self):
        self.core.library.refresh('dummy2:a')

        self.assertFalse(self.library1.refresh.called)
        self.library2.refresh.assert_called_once_with('dummy2:a')

    def test_refresh_without_uri_calls_all_backends(self):
        self.core.library.refresh()

        self.library1.refresh.assert_called_once_with(None)
        self.library2.refresh.assert_called_once_with(None)

    def test_find_exact_combines_results_from_all_backends(self):
        track1 = Track(uri='dummy1:a')
        track2 = Track(uri='dummy2:a')
        self.library1.find_exact().get.return_value = Playlist(tracks=[track1])
        self.library1.find_exact.reset_mock()
        self.library2.find_exact().get.return_value = Playlist(tracks=[track2])
        self.library2.find_exact.reset_mock()

        result = self.core.library.find_exact(any=['a'])

        self.assertIn(track1, result.tracks)
        self.assertIn(track2, result.tracks)
        self.library1.find_exact.assert_called_once_with(any=['a'])
        self.library2.find_exact.assert_called_once_with(any=['a'])

    def test_search_combines_results_from_all_backends(self):
        track1 = Track(uri='dummy1:a')
        track2 = Track(uri='dummy2:a')
        self.library1.search().get.return_value = Playlist(tracks=[track1])
        self.library1.search.reset_mock()
        self.library2.search().get.return_value = Playlist(tracks=[track2])
        self.library2.search.reset_mock()

        result = self.core.library.search(any=['a'])

        self.assertIn(track1, result.tracks)
        self.assertIn(track2, result.tracks)
        self.library1.search.assert_called_once_with(any=['a'])
        self.library2.search.assert_called_once_with(any=['a'])
