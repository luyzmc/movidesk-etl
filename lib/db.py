import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')


def fetchone(query: str):
    conn = None
    cur = None
    result = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchone()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

    return result


def execute(query: str):
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()


def create_table_movidesk_questions():
    execute("""create table movidesk_questions(
        id varchar(20) not null,
        is_active boolean not null,
        type int not null,
        description varchar(255)
    )""")
    execute("""create unique index movidesk_questions_id_uindex on movidesk_questions (id)""")
    execute("""alter table movidesk_questions add constraint movidesk_questions_pk primary key (id)""")


def create_table_movidesk_responses():
    execute("""create table movidesk_responses(
        id varchar(20) not null,
        question_id varchar(20) not null,
        type int not null,
        ticket_id int not null,
        client_id varchar(25) not null,
        response_date timestamp not null,
        value int,
        commentary text
    )""")
    execute("""create unique index movidesk_responses_id_uindex on movidesk_responses (id)""")
    execute("""alter table movidesk_responses add constraint movidesk_responses_pk primary key (id)""")
    execute("""alter table movidesk_responses 
        add constraint movidesk_responses_movidesk_questions_id_fk 
        foreign key (question_id) references movidesk_questions""")
