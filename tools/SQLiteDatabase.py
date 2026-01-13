from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, create_engine, Session, select, inspect

import os
from dotenv import load_dotenv
load_dotenv()


# Define the data model
class News(SQLModel, table=True):
    news_id: str = Field(primary_key=True, unique=True) # 👈 Enforce uniqueness
    title: str
    published_date: str
    published_time: str
    source_url: str
    content: str
    summary: Optional[str] = Field(default=None)
    total_chunks: Optional[int] = Field(default=None)
    keywords: Optional[str] = Field(default=None)


class sqliteHandler:
    def __init__(self, logger):
        self.logger=logger
        self.DBname=os.getenv("SQLITE_FILENAME")
        self.sqlite_url = f"sqlite:///{self.DBname}"
        self.engine=create_engine(self.sqlite_url)
        self.logger.info(f"Class - {sqliteHandler.__name__} initiated.")
        
        
    def check_and_create_table(self) -> None:
        inspector = inspect(self.engine)
        if inspector.has_table("News"):
            self.logger.info("Table News already exists.")
        else:
            self.logger.info("Table News does not exist, creating it now.")
            SQLModel.metadata.create_all(self.engine)
            self.logger.info("Table News created.")
        return None


    def create_news(self, news_item: News) -> None:
        with Session(self.engine) as session:
            statement = select(News).where(News.news_id == news_item.news_id)
            existing = session.exec(statement=statement).first()
            if not existing:
                session.add(news_item)
                session.commit()
                session.refresh(news_item)
                self.logger.info(f"News - title: {news_item.title} (id: {news_item.news_id}) saved to sqlite3.")   
        
        return None

    def read_news(self, news_id: str):
        with Session(self.engine) as session:
            return session.get(News, news_id)

    def update_news(self, news_id: str, update_data: dict):
        with Session(self.engine) as session:
            db_news = session.get(News, news_id)
            if not db_news:
                return None
            for key, value in update_data.items():
                setattr(db_news, key, value)
            session.add(db_news)
            session.commit()
            session.refresh(db_news)
            
            return db_news

    def delete_news(self, news_id: str):
        with Session(self.engine) as session:
            db_news = session.get(News, news_id)
            if db_news:
                session.delete(db_news)
                session.commit()
                return True
            return False

    def list_all_news(self):
        with Session(self.engine) as session:
            return session.exec(select(News)).all()

    def list_all_news_id(self):
        with Session(self.engine) as session:
            return session.exec(select(News.news_id)).all()
    
## usage example

# handler = sqliteHandler("news_data.db")

# # Create
# new_entry = News(
#     title="2026 Tech Trends", 
#     publish_date=date(2026, 1, 9), 
#     publish_time=time(14, 30),
#     source_url="https://example.com",
#     content="Full article content...",
#     keywords="AI, Tech, Future"
# )
# handler.create_news(new_entry)

# # Read
# news = handler.read_news(1)
# print(news.title if news else "Not Found")