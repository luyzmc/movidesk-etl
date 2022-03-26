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


def capture_responses():
    _has_more = True
    _last = ''
    _i = 0
    while _has_more:
        responses_text = movidesk.responses(_last)
        responses = json.loads(responses_text)
        _has_more = responses.get('hasMore')
        for response in responses.get('items'):

            _id = response.get("id")
            _question_id = response.get("questionId")
            _type = response.get("type")
            _ticket_id = response.get("ticketId")
            _client_id = response.get("clientId")
            _response_date = response.get("responseDate")
            _commentary = response.get("commentary")
            _value = response.get("value")

            result = db.fetchone(f"SELECT id FROM movidesk_responses where id = '{_id}'")

            __value = _value if _value is not None else "null"
            __commentary = f"'{_commentary.encode('string_escape')}'" if _commentary is not None else "null"
            if result is None:
                db.execute(f"""INSERT INTO movidesk_responses 
                           (id, question_id, type, ticket_id, client_id, response_date, value, commentary) 
                    VALUES ('{_id}', '{_question_id}', {_type}, {_ticket_id}, '{_client_id}', '{_response_date}', 
                           {__value}, {__commentary})""")
            else:
                db.execute(f"""UPDATE movidesk_responses SET
                                    question_id = '{_question_id}',
                                    type = {_type},
                                    ticket_id = {_ticket_id},
                                    client_id = '{_client_id}',
                                    response_date = '{_response_date}',
                                    value = {__value},
                                    commentary = {__commentary}
                                    WHERE id = '{_id}'""")

            _i += 1
            print(f"{_i}: {_id}, {_question_id}, {_type}, {_ticket_id}, {_client_id}, "
                  f"{_response_date}, {_value}, {_commentary}")
            _last = _id


if __name__ == '__main__':
    # db.create_table_movidesk_questions()
    # db.create_table_movidesk_responses()
    capture_questions()
    capture_responses()
