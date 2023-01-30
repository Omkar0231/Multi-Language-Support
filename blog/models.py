from MultiLang import custom_models as models


class Article(models.Model):
    title = models.MultiLanguageJSONField()
    test_lang = models.MultiLanguageJSONField()

    def __str__(self):
        return str(self.id)


# Testing by creating a new model if the created Multi Language Field works in admin panel.
class Author(models.Model):
    author = models.MultiLanguageJSONField()

    def __str__(self):
        return str(self.id)
