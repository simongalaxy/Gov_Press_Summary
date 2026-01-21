from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, select, inspect
from sqlalchemy import Column, String, Date, Time
from sqlalchemy.dialects.postgresql import ARRAY

import datetime
from pprint import pformat
import os
from dotenv import load_dotenv
load_dotenv()


class News(SQLModel, table=True):
    id: str = Field(primary_key=True, unique=True, description="News id")
    url: str = Field(description="link of press release")
    title: str = Field(default=None, description="title of the press release")
    pub_date: str = Field(default=None, description="Published date")
    pub_time: str = Field(default=None, description="Published time")
    content: str = Field(description="Content of the press release")
    summary: Optional[str] = Field(default=None, description="summary of the press release")
    keyword: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)), description="keyword of the press release")
    total_chunks: Optional[int] = Field(default=None, description="Number of chunks")
    

class PostgresDBHandler:
    def __init__(self, logger):
        self.logger=logger
        self.username = os.getenv("username")
        self.password = os.getenv("password")
        self.host = os.getenv("host")
        self.port = os.getenv("port")
        self.db_name = os.getenv("db_name")
        self.postgres_url = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        self.engine=create_engine(self.postgres_url, echo=True)
        
        self.logger.info(f"Class - {PostgresDBHandler.__name__} initiated.")
        
        
    def check_and_create_table(self) -> None:
        inspector = inspect(self.engine)
        if inspector.has_table(self.db_name):
            self.logger.info(f"Table {self.db_name} already exists.")
        else:
            self.logger.info(f"Table {self.db_name} does not exist, creating it now.")
            SQLModel.metadata.create_all(self.engine)
            self.logger.info(f"Table {self.db_name} created.")
        
        return None


    def create_News(self, news_item: News) -> None:
        with Session(self.engine) as session:
            statement = select(News).where(News.id == news_item.id)
            existing = session.exec(statement=statement).first()
            if not existing:
                session.add(news_item)
                session.commit()
                session.refresh(news_item)
                self.logger.info(f"News - id: {news_item.id}) saved to sqlite3.")
            else:
                self.logger.info(f"News - id: {news_item.id} item already existed in database. No saving action taken.")   
        
        return None

    
    def read_News(self, id: str):
        with Session(self.engine) as session:
            return session.get(News, id)


    def update_News(self, id: str, update_data: dict):
        with Session(self.engine) as session:
            db_News = session.get(News, id)
            if not db_News:
                return None
            for key, value in update_data.items():
                setattr(db_News, key, value)
            session.add(db_News)
            session.commit()
            session.refresh(db_News)
            
            return


    def delete_News(self, id: str):
        with Session(self.engine) as session:
            db_News = session.get(News, id)
            if db_News:
                session.delete(db_News)
                session.commit()
                return True
            return False


    def list_all_News(self):
        with Session(self.engine) as session:
            return session.exec(select(News)).all()
    
    
    def save_news_to_db(self, news_list) -> None:
        # save all crawled data:
        self.logger.info("Save crawled data into Postgresql DB.")
        for news in news_list:
            news_item = News(
                id=news.url.split("/")[-1].replace(".htm", ""),
                title=news.metadata["title"],
                pub_date=news.markdown.split("\n")[-4].split(", ", 1)[-1].strip(),
                pub_time=news.markdown.split("\n")[-3].split(" ")[-2],
                url=news.url,
                content=news.markdown
            )
            self.create_News(news_item=news_item)
        self.logger.info(f"Saved total {len(news_list)} jobDBs into Postgresql.")
        
        return None
            
