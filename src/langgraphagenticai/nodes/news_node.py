import os
from typing import Literal, cast
from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate

from src.langgraphagenticai.state.news_state import Frequency, NewsState

TimeRange = Literal["day", "week", "month", "year"]

class NewsNode:
    def __init__(self,llm):
        """
        Inicializa el NewsNode con las claves API para Tavily.
        """
        self.tavily = TavilyClient()
        self.llm = llm
        

    def fetch_news(self, state: NewsState):
        """
        Obtiene noticias del tema en la frecuencia especificada.
        
        Args:
            state (dict): El diccionario de estado que contiene 'frequency' y 'topic'.
        
        Returns:
            dict: Estado actualizado con la clave 'news_data' que contiene las noticias obtenidas.
        """
        frequency = state['frequency']
        topic = state['topic']
        if frequency not in {'daily', 'weekly', 'monthly', 'yearly'}:
            raise ValueError("Frecuencia no válida. Debe ser 'daily', 'weekly', 'monthly' o 'yearly'.")
        time_range_map: dict[Frequency, TimeRange] = {'daily': 'day', 'weekly': 'week', 'monthly': 'month', 'yearly': 'year'}
        time_range = time_range_map[frequency]  
        days_map = {'daily': 1, 'weekly': 7, 'monthly': 30, 'yearly': 366}

        response = self.tavily.search(
            query=f"Noticias principales de {topic} en España y a nivel global",
            time_range=time_range,
            include_answer="advanced",
            max_results=15,
            days=days_map[frequency],
        )
        news_data = list(response.get('results', []))
        return {
            'news_data': news_data,
        }

    def summarize_news(self, state: NewsState):
        """
        Resume las noticias obtenidas usando un LLM.
        
        Args:
            state (dict): El diccionario de estado que contiene 'news_data'.
        
        Returns:
            dict: Estado actualizado con la clave 'summary' que contiene el resumen de las noticias.
        """
        news_items = state['news_data'] or []
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Resume los artículos de noticias de {topic} en formato markdown. Para cada elemento incluye:
            - Fecha en formato **YYYY-MM-DD** en la zona horaria IST
            - Resumen conciso de las últimas noticias en oraciones
            - Ordenar las noticias por fecha (las más recientes primero)
            - URL de la fuente como enlace
            - Si una noticia no está relacionada con el tema {topic}, omitirla del resumen
            Usa el formato:
            ### [Fecha]
            - [Resumen](URL)"""),
            ("user", "Artículos:\n{articles}")
        ])
        
        articles_str = "\n\n".join([
            f"Contenido: {item.get('content', '')}\nURL: {item.get('url', '')}\nFecha: {item.get('published_date', '')}"
            for item in news_items
        ])
        
        response = self.llm.invoke(prompt_template.format(articles=articles_str, topic=state['topic']))
        state['summary'] = response.content
        return {
            'summary': state['summary']
        }
    
    def save_result(self, state: NewsState):
        topic = state['topic']
        frequency = state['frequency']
        summary = state['summary'] or "No se encontraron noticias para resumir."
        # Si no existe el directorio, lo crea
        os.makedirs("./news", exist_ok=True)
        filename = f"./news/{topic}-{frequency}_summary.md"
        with open(filename, 'w') as f:
            f.write(f"# Resumen de Noticias de {topic.capitalize()} {frequency.capitalize()}\n\n")
            f.write(summary)
        return {
            'filename': filename
        }
