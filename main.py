from lib import movidesk, db
import json


def capture_questions():
    questions_text = movidesk.questions()
    questions = json.loads(questions_text)
    for question in questions:
        _id = question.get('id')
        _is_active = question.get('isActive')
        _type = question.get('type')
        languages = question.get('languages')
        language = None
        for _language in languages:
            if _language.get('cultureId') == 'pt-BR':
                language = _language
        _description = language.get('description')

        result = db.fetchone(f"SELECT id FROM movidesk_questions where id = '{_id}'")
        if result is None:
             db.execute(f"""INSERT INTO movidesk_questions (id, is_active, type, description) 
                            VALUES ('{_id}', {_is_active}, {_type}, '{_description}')""")
        else:
             db.execute(f"""UPDATE movidesk_questions SET 
                                is_active = {_is_active}, 
                                type = {_type}, 
                                description = '{_description}' 
                                WHERE id = '{_id}'""")
        print(f"{_id}, {_type}, {_is_active}, {_description}")


if __name__ == '__main__':
    # db.create_table_movidesk_questions()
    capture_questions()
