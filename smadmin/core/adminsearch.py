from . import html


class ListViewSearch(object):
    def __init__(self, post_params):
        self._form = self.form(**post_params)

    def form(self, **post_params):
        raise NotImplementedError

    def filter(self, data, cursor):
        raise NotImplementedError


class DefaultListViewSearch(ListViewSearch):
    title = 'Search'

    def form(self, **post_params):
        return html.Form(
            html.InputGoup(
                html.Input(
                    name='search_default',
                    placeholder='Search by ID or GQL',
                    value=post_params.get('search_default')
                )
            )
        )

    def filter(self, data, cursor):
        if 'search_default' in data:
            pass
