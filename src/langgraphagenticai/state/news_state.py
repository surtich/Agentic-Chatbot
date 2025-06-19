from typing import Annotated, List, Literal, Optional
from typing_extensions import TypedDict

Frequency = Literal['daily', 'weekly', 'monthly', 'yearly']
NewsItem = TypedDict('NewsItem', {
    'title': str,
    'url': str,
    'published_date': str,
    'content': str
})

class NewsState(TypedDict):
    """
     Representa el estado del grafo de noticias
    """
    topic: str
    frequency: Frequency
    news_data: Optional[List[NewsItem]]
    summary: Optional[str]
    filename: Optional[str]