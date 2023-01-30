import json

from collections import defaultdict
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib import admin
from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError

from MultiLang.custom_models import MultiLanguageJSONField
from blog import constants as blog_constants


VALIDATION_REQUIRED_ERROR = ValidationError('Missing data.', code='required')


def get_converted_language_field_name(field_name, lang_code):
    """
    This method converts field name to the Language Field name.
    :param field_name: The field name i.e., title, name, etc.
    :param lang_code: The language code i.e., 'en', 'fr', etc.
    :return: string with the new field name to show in admin page. Ex: Title (e)
    """
    return f'{field_name.title()} ({lang_code})'


def get_default_language_text(field_name):
    """

    :param field_name: The field name i.e., title, name, etc.
    :return: The default field(choice field to select the default language for that field.) text i.e.,
    title_default_language
    """
    return blog_constants.IS_DEFAULT_TEXT.format(field_name)


def get_multilang_field_names(model, accepted_fields=None, with_field_name=False):
    """
    This function returns the all the newly created Language fields.
    :param model: The model Object.
    :param accepted_fields: The list of fields which are mentioned in the fieldsets.
    :param with_field_name: It returns dictionary with the model field_name as key and newly created
    Language fields as values.
    :return: {
        "FIELD_NAME": {"LANGUAGE_FIELD": "LANGUAGE_CODE"}
    }
    Ex: {
    "title": {"Title (en)": "en"}
    }
    """
    if accepted_fields is None:
        accepted_fields = set()

    multi_lang_fields_names = {} if with_field_name else []

    for model_field in model._meta.fields:
        if accepted_fields and model_field.name not in accepted_fields:
            continue
        if type(model_field) is MultiLanguageJSONField:
            # If with_field_name is true, we will be returning teh dictionary where keys are the model fields names and
            # their values are newly created language fields.
            if with_field_name:
                multi_lang_fields_names[model_field.name] = {
                    get_converted_language_field_name(model_field.name, code): code
                    for code, language in settings.LANGUAGES
                }
                # Adding {FIELD_NAME}_default_language as choice field to make the user to select a default value.
                # Setting the initial value to english.
                multi_lang_fields_names[model_field.name].update({
                    get_default_language_text(model_field.name): settings.DEFAULT_LANGUAGE_CODE
                })
            else:
                multi_lang_fields_names += [f'{model_field.name.title()} ({code})'
                                            for code, language in settings.LANGUAGES]
    return multi_lang_fields_names


class MultiLangForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MultiLangForm, self).__init__(*args, **kwargs)
        self.multilang_field_names = get_multilang_field_names(
            self._meta.model, accepted_fields=set(self.fields.keys()), with_field_name=True
        )

        instance = kwargs['instance'] if 'instance' in kwargs else None
        for field_name, lang_field_names in self.multilang_field_names.items():
            # Making the Original field names read-only just to cross-check the values.
            self.fields[field_name].widget.attrs['readonly'] = blog_constants.READ_ONLY_ATTRIBUTE
            self.fields[field_name].help_text = blog_constants.READ_ONLY_FIELD_HELP_TEXT

            for lang_field_name, lang_code in lang_field_names.items():
                self.fields[lang_field_name] = forms.ChoiceField(
                    choices=settings.LANGUAGES, required=False, initial=settings.DEFAULT_LANGUAGE
                ) if lang_code is settings.DEFAULT_LANGUAGE_CODE else forms.CharField(required=False)
                if instance:
                    data = getattr(instance, field_name)
                    if data:
                        self.fields[lang_field_name].initial = data.get(lang_code, '')

    def clean(self):
        """
        This method is overwritten to validate if the default_language is given some value.
        :return: cleaned_data
        """
        errors = {}
        for field_name in self.multilang_field_names.keys():
            is_default_field_name = get_default_language_text(field_name)
            is_default_lang_code = self.data[is_default_field_name]

            # The data is converted to json to check if the default value is given or not.
            value = json.loads(self.data.get(field_name, "{}"))
            if not value or not value[is_default_lang_code]:
                errors[get_converted_language_field_name(field_name, is_default_lang_code)] = VALIDATION_REQUIRED_ERROR

        if errors:
            raise ValidationError(errors)

        return self.cleaned_data


class MultiLangAdmin(admin.ModelAdmin):
    form = MultiLangForm

    def __init__(self, model, admin_site):
        self.multilang_field_names = {}
        if not self.fieldsets:
            self.fieldsets = (None, {blog_constants.FIELDS_TEXT: [field.name for field in model._meta.get_fields()
                                                                  if not field.name == 'id']}),
        super().__init__(model, admin_site)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['fields'] = flatten_fieldsets(self.fieldsets)
        multilang_data = defaultdict(dict)

        # If POST request, modifying the data to be suitable for the form.
        if request.POST:
            data = request.POST
            for field_name, lang_field_names in self.multilang_field_names.items():
                for lang_field_name, lang_code in lang_field_names.items():
                    get_default_language_text(lang_field_name)
                    multilang_data[field_name][lang_code] = data[lang_field_name]

            data._mutable = True
            # Converting the final data before saving to the model
            for field_name, value in multilang_data.items():
                # Here, we are converting it to json to get rid of the single quotes and double quotes issue.
                data[field_name] = str(json.dumps(value))

        return super(MultiLangAdmin, self).get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(MultiLangAdmin, self).get_fieldsets(request, obj)
        new_fieldsets = list(fieldsets)
        self.multilang_field_names = get_multilang_field_names(
            self.model, accepted_fields=set(flatten_fieldsets(new_fieldsets)), with_field_name=True
        )

        # Appending the newly created fields i.e., Title (en), etc. are being appended to the fieldsets with the Name
        # as the Sub Heading in the Admin panel.
        for field_name, lang_field_names in self.multilang_field_names.items():
            new_fieldsets.append([" ".join(field_name.split("_")).title(), {
                blog_constants.FIELDS_TEXT: [lang_field_name for lang_field_name in lang_field_names.keys()]
            }])

        return new_fieldsets


def register(model, model_admin=None):
    """
    This is our custom register function to register the models in the admin. Using this function to register
    the Models automatically detects the Multi Language Fields and show as required in the admin panel.
    :param model: Model Instance
    :param model_admin: the ModelAdmin class if they need any custom Choice of Admin Panel.
    :return: None
    """
    admin.site.register(model, model_admin if model_admin else MultiLangAdmin)
