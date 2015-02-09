import os

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

from .errors import AbstractClassError


class EntityForm(object):
    TEMPLATE_PATH = os.path.join(
        os.path.dirname(__file__),
        '../templates/form/form.html'
    )

    def __init__(self, admin_model, entity):
        self.admin_model = admin_model
        self.entity = entity
        self.form = []

        if self.admin_model.detail_display:
            for k in self.admin_model.detail_display:
                v = getattr(self.entity.__class__, k, None)
                # TODO: Handle misconfiguration (k not a property of entity)
                if v is None:
                    # Skip unknown property names
                    continue
                property_form_cls = self._get_property_form_for_ndb_property(v)
                property_form = property_form_cls(
                    entity,
                    k,
                    readonly=k in self.admin_model.detail_readonly
                )
                if property_form is not None:
                    self.form.append(property_form)
        else:
            for k, v in entity.__class__.__dict__.iteritems():
                if not isinstance(v, ndb.Property):
                    continue
                property_form_cls = self._get_property_form_for_ndb_property(v)
                property_form = property_form_cls(
                    entity,
                    k,
                    readonly=k in self.admin_model.detail_readonly
                )
                if property_form is not None:
                    self.form.append(property_form)

    def _get_property_form_for_ndb_property(self, ndb_property):
        if isinstance(ndb_property, ndb.IntegerProperty):
            return IntegerPropertyForm
        elif isinstance(ndb_property, ndb.StringProperty):
            return StringPropertyForm
        elif isinstance(ndb_property, ndb.TextProperty):
            return TextPropertyForm
        elif isinstance(ndb_property, ndb.DateTimeProperty):
            return DatetimePropertyForm
        return None

    def __str__(self):
        return template.render(
            self.__class__.TEMPLATE_PATH,
            {'form': self.form}
        )


class PropertyForm(object):
    def __init__(self, entity, property_name, *args, **kwargs):
        if self.__class__ == PropertyForm:
            raise AbstractClassError(self.__class__)
        self.entity = entity
        self.property_name = property_name
        self.readonly = 'readonly' in kwargs and kwargs['readonly']

    def __str__(self):
        return template.render(
            self.__class__.TEMPLATE_PATH,
            {
                'entity': self.entity,
                'property_name': self.property_name,
                'readonly': self.readonly,
            }
        )


class IntegerPropertyForm(PropertyForm):
    TEMPLATE_PATH = os.path.join(
        os.path.dirname(__file__),
        '../templates/form/integer_property.html'
    )


class StringPropertyForm(PropertyForm):
    TEMPLATE_PATH = os.path.join(
        os.path.dirname(__file__),
        '../templates/form/string_property.html'
    )


class TextPropertyForm(PropertyForm):
    TEMPLATE_PATH = os.path.join(
        os.path.dirname(__file__),
        '../templates/form/text_property.html'
    )


class DatetimePropertyForm(PropertyForm):
    TEMPLATE_PATH = os.path.join(
        os.path.dirname(__file__),
        '../templates/form/datetime_property.html'
    )


class KeyPropertyForm(PropertyForm):
    pass
