import pykka

from mopidy.models import Playlist


class LibraryController(object):
    pykka_traversable = True

    def __init__(self, backends, core):
        self.backends = backends
        uri_schemes_by_backend = {backend: backend.uri_schemes.get()
            for backend in backends}
        self.backends_by_uri_scheme = {uri_scheme: backend
            for backend, uri_schemes in uri_schemes_by_backend.items()
            for uri_scheme in uri_schemes}

        self.core = core

    def _get_backend(self, uri):
        uri_scheme = uri.split(':', 1)[0]
        return self.backends_by_uri_scheme.get(uri_scheme)

    def find_exact(self, **query):
        """
        Search the library for tracks where ``field`` is ``values``.

        Examples::

            # Returns results matching 'a'
            find_exact(any=['a'])
            # Returns results matching artist 'xyz'
            find_exact(artist=['xyz'])
            # Returns results matching 'a' and 'b' and artist 'xyz'
            find_exact(any=['a', 'b'], artist=['xyz'])

        :param query: one or more queries to search for
        :type query: dict
        :rtype: :class:`mopidy.models.Playlist`
        """
        futures = []
        for backend in self.backends:
            futures.append(backend.library.find_exact(**query))
        results = pykka.get_all(futures)
        return Playlist(tracks=[
            track for playlist in results for track in playlist.tracks])

    def lookup(self, uri):
        """
        Lookup track with given URI. Returns :class:`None` if not found.

        :param uri: track URI
        :type uri: string
        :rtype: :class:`mopidy.models.Track` or :class:`None`
        """
        backend = self._get_backend(uri)
        if backend:
            return backend.library.lookup(uri).get()

    def refresh(self, uri=None):
        """
        Refresh library. Limit to URI and below if an URI is given.

        :param uri: directory or track URI
        :type uri: string
        """
        if uri is not None:
            backend = self._get_backend(uri)
            if backend:
                return backend.library.refresh(uri).get()
        else:
            futures = []
            for backend in self.backends:
                futures.append(backend.library.refresh(uri))
            return pykka.get_all(futures)

    def search(self, **query):
        """
        Search the library for tracks where ``field`` contains ``values``.

        Examples::

            # Returns results matching 'a'
            search(any=['a'])
            # Returns results matching artist 'xyz'
            search(artist=['xyz'])
            # Returns results matching 'a' and 'b' and artist 'xyz'
            search(any=['a', 'b'], artist=['xyz'])

        :param query: one or more queries to search for
        :type query: dict
        :rtype: :class:`mopidy.models.Playlist`
        """
        futures = []
        for backend in self.backends:
            futures.append(backend.library.search(**query))
        results = pykka.get_all(futures)
        return Playlist(tracks=[
            track for playlist in results for track in playlist.tracks])
