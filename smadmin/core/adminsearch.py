from . import html
from .errors import AbstractClassError


class ListViewSearch(object):
    title = None
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
        self._form.children.append(
            html.Div(
                html.Input(type_='hidden', name='search'),
                class_='input-group',
            )
        )

    def form(self, **GET_params):
        raise NotImplementedError

    def search(self, data, cursor):
        raise NotImplementedError


class DefaultListViewSearch(ListViewSearch):
    title = 'Search'
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
                    placeholder=self.__class__.title,
                    value=GET_params.get(
                        '{}_value'.format(self.__class__.name)
                    ),
                    class_='form-control input-lg'
                ),
                class_='input-group',
            )
        )

    def search(self, data, cursor):
        if 'search_default' in data:
            pass
