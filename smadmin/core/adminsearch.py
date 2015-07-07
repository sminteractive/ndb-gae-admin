import re

from . import html
from .errors import AbstractClassError
from .errors import EmptySearchError


class ListViewSearch(object):
    title = None
    placeholder = title
    name = None

    def __init__(self, **GET_params):
        if self.__class__ == ListViewSearch:
            raise AbstractClassError(self.__class__)

        for attribute in (self.__class__.title, self.__class__.name):
            if not attribute:
                raise ValueError(
                    '{}.{} attribute must be a string, and cannot be None or '
                    'empty'.format(
                        self.__class__.__name__,
                        attribute.__name__
                    )
                )

        self._form = self.form(**GET_params)
        # Create an invisible input in the form so we know which search class
        # is being used when the admin receives the form data.
        self._form.children.append(
            html.Div(
                html.Input(
                    type_='hidden',
                    name='search',
                    value=self.__class__.name
                ),
                class_='input-group',
            )
        )

    def form(self, **GET_params):
        raise NotImplementedError

    @classmethod
    def search(self, data, cursor):
        raise NotImplementedError


class DefaultListViewSearch(ListViewSearch):
    title = 'Search'
    placeholder = 'Search by ID or GQL Query'
    name = 'default_search'

    def form(self, **GET_params):
        return html.Form(
            html.Div(
                html.Span(
                    html.Button(
                        'Go!',
                        class_='btn btn-primary input-lg',
                        type_='submit',
                    ),
                    class_='input-group-btn'
                ),
                html.Input(
                    name='{}_value'.format(self.__class__.name),
                    placeholder=self.__class__.placeholder,
                    value=GET_params.get(
                        '{}_value'.format(self.__class__.name)
                    ),
                    class_='form-control input-lg'
                ),
                class_='input-group',
            )
        )

    @classmethod
    def search(cls, model, data, cursor):
        search_value = data.get('{}_value'.format(cls.name))
        if not search_value:
            raise EmptySearchError()

        results = []
        _r = model.get_by_id(search_value)
        if _r is None:
            try:
                search_value_int = int(search_value)
                _r = model.get_by_id(search_value_int)
                results.append(_r)
            except Exception:
                pass
        else:
            results.append(_r)

        # If we haven't found any entity by ID, search using a GQL Query
        if not results:
            try:
                query = model.gql('WHERE ' + search_value)
                count = 50
                itr = query.iter(
                    start_cursor=cursor,
                    produce_cursors=True,
                    batch_size=count,
                )
                i = 0
                while itr.has_next():
                    if i >= count:
                        break
                    _next = itr.next()
                    results.append(_next)
                    i += 1

                # Prepare the return values
                more = itr.probably_has_next()
                next_cursor = itr.cursor_after() if more else None
            except Exception:
                pass
            else:
                return results, next_cursor, more

        return results, None, False
