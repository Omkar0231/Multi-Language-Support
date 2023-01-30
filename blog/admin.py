from MultiLang.custom_admin import register
from .models import Article, Author

# I have made a new function register which when used, Multi Language Fields are
# displayed as required in django admin panel.
register(Article)
register(Author)
