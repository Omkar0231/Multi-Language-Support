from django.conf import settings
from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
from django.urls import reverse

from MultiLang.custom_admin import get_multilang_field_names, get_default_language_text
from MultiLang.utils import generate_random_string
from blog.models import Article


def get_admin_change_view_url(obj):
    return reverse(
        'admin:{}_{}_change'.format(
            obj._meta.app_label,
            type(obj).__name__.lower()
        ),
        args=(obj.id,)
    )


def get_admin_add_view_url(model):
    return reverse(
        'admin:{}_{}_add'.format(
            model._meta.app_label,
            model.__name__.lower()
        )
    )


class TestGroupAdmin(TestCase):
    @classmethod
    def get_client(cls):
        """
        This is to create the client with a logged in user.
        :return: client object
        """
        username, password, email = 'om', '2311', 'om@gmail.com'
        # prepare client
        if not User.objects.filter(username='om').exists():
            User.objects.create_superuser(
                username=username, password=password, email=email
            )
        c = Client()
        c.login(username=username, password=password)
        return c

    def create_article_object(self):
        """
        creates the article object. This is also used while getting the object.
        :return: response
        """
        post_data = {}
        RANDOM_STRING_SIZE = 10
        # Creating post_data
        for field_name, lang_field_names in get_multilang_field_names(Article, with_field_name=True).items():
            for lang_field_name, lang_code in lang_field_names.items():
                if lang_code == settings.DEFAULT_LANGUAGE_CODE:
                    post_data[lang_field_name] = settings.DEFAULT_LANGUAGE
                    continue
                post_data[lang_field_name] = generate_random_string(RANDOM_STRING_SIZE)

        client = self.get_client()
        # Creating the Article
        response = client.post(get_admin_add_view_url(Article), data=post_data, follow=True)
        return response

    def test_add_view_loads_normally(self):
        """
        Testing the Adding Article Admin Page
        :return: None
        """
        response = self.create_article_object()
        errors = response.context_data["errors"] if "errors" in response.context else None
        self.assertEqual(errors, None)
        # run test
        self.assertEqual(response.status_code, 200)

    def test_change_view_loads_normally(self):
        """
        Testing the Changing Article Admin Page
        :return: None
        """
        self.create_article_object()
        article = Article.objects.first()

        client = self.get_client()
        response = client.get(get_admin_change_view_url(article))
        self.assertEqual(response.status_code, 200)

