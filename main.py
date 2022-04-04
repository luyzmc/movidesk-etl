from datetime import datetime

from lib import movidesk
from lib.db import DB
import json



def create_tables():
    db = DB.connect()
    # movidesk_questions
    db.execute("""create table movidesk_questions(
        id varchar(20) not null,
        is_active boolean not null,
        type int not null,
        description varchar(255)
    )""")
    db.execute("""create unique index movidesk_questions_id_uindex on movidesk_questions (id)""")
    db.execute("""alter table movidesk_questions add constraint movidesk_questions_pk primary key (id)""")

    # movidesk_responses
    db.execute("""create table movidesk_responses(
        id varchar(20) not null,
        question_id varchar(20) not null,
        type int not null,
        ticket_id int not null,
        client_id varchar(25) not null,
        response_date timestamp not null,
        value int,
        commentary text
    )""")
    db.execute("""create unique index movidesk_responses_id_uindex on movidesk_responses (id)""")
    db.execute("""alter table movidesk_responses add constraint movidesk_responses_pk primary key (id)""")
    db.execute("""alter table movidesk_responses
        add constraint movidesk_responses_movidesk_questions_id_fk
        foreign key (question_id) references movidesk_questions""")

    db.execute("""create table movidesk_status_histories(
        ticket_id int not null,
        status varchar(50) not null,
        justification varchar(50),
        changed_date timestamp not null,
        full_time decimal,
        working_time decimal
    )""")
    db.commit()
    db.disconect()

# centralizando perguntas da pesquisa de satisfação
def capture_questions():
    questions_text = movidesk.questions()
    questions = json.loads(questions_text)
    db = DB.connect()
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
    db.commit()
    db.disconect()

# centralizando Respostas da pesquisa de satisfação
def capture_responses(only_news=False):
    _has_more = True                              # Parametro inicial para ver se tem mais paginas para serem consultadas na API
    _last = ''                                    # Parametro inicial para lembrar do ultimo id quando estiver trocando de pagina
    _last_response_date = ''                      # Parametro inicial para data da ultima respsta em banco
    db = DB.connect()                             # Abre conexão com banco de dados para consultar a ultima data de resposta e fazer os updates ou insert necessarios.
    if only_news:                                 # Verificar no banco de dados a ultima data de resposta e armazena em uma variavel
        resp = db.fetchone('select response_date from movidesk_responses order by response_date desc limit 1')
        if resp is not None:
            _last_response_date = resp[0]
    _i = 0                                        # Contagem de linhas que estão sendo inseridas
    while _has_more:                              # Enquanto _has_more = true consulte as paginas
        responses_text = movidesk.responses(_last, str(_last_response_date).replace(' ', 'T')) # variavel armazena os dados obtidos via API
        responses = json.loads(responses_text)    # Função que transforma os dados obtidos em um Json
        _has_more = responses.get('hasMore')      # Variavel recebe true ou false da cunsulta
        for response in responses.get('items'):   # Para cada Resposta(items) verifique as informações abaixo e armazene na variavel correspondente

            _id = response.get("id")
            _question_id = response.get("questionId")
            _type = response.get("type")
            _ticket_id = response.get("ticketId")
            _client_id = response.get("clientId")
            _response_date = response.get("responseDate")
            _commentary = response.get("commentary")
            _value = response.get("value")

            result = db.fetchone(f"SELECT id FROM movidesk_responses where id = '{_id}'") # Variavel recebe a função do select de verificar o id no BD

            __value = _value if _value is not None else "null"            # consertando visualização da nota - de "None" para "null"
            __commentary = f"'{_commentary.encode('utf-8').decode('unicode-escape')}'" if _commentary is not None else "null" # consertando comentarios fora do padrão, em branco ou com pular linha.
            if result is None:                                            # if para testar se o id recebido já existe no BD - nesse caso se não existir, chama a função de inserir a linha.
                db.execute(f"""INSERT INTO movidesk_responses 
                           (id, question_id, type, ticket_id, client_id, response_date, value, commentary) 
                    VALUES ('{_id}', '{_question_id}', {_type}, {_ticket_id}, '{_client_id}', '{_response_date}', 
                           {__value}, {__commentary})""")
            else:                                                         # se não, ele faz um update, atualizando a informação existente.
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
            print(f"{_i}: {_id}, {_question_id}, {_type}, {_ticket_id}, {_client_id}, "     # escreve o que está sendo inserido
                  f"{_response_date}, {_value}, {_commentary}")

            _last = _id                                                                     # gravando o ultimo id recebido para dar continuidade na proxima pagina
        db.commit()                                                                         # comita no BD o que foi encontrado
    db.disconect()                                                                          # desconecta do BD


def capture_status_histories():
    _i = 0
    _has_more = True
    _last = ''
    db = DB.connect()
    resp = db.fetchone('select changed_date from movidesk_status_histories order by changed_date desc limit 1')
    if resp is not None:
       _last = str(resp[0])
    while _has_more:
        tickets_text = movidesk.status_histories(_i, _last.replace(' ', 'T'))
        tickets = json.loads(tickets_text)
        _has_more = len(tickets) == 1000

        for ticket in tickets:
            ticket_id = ticket.get("id")
            status_histories = ticket.get("statusHistories")
            _i += 1
            for status_historic in status_histories:
                _status = status_historic.get("status")
                _justification = status_historic.get("justification")
                _changedDate = status_historic.get("changedDate")
                _full_time = status_historic.get("permanencyTimeFullTime")
                _workingTime = status_historic.get('permanencyTimeWorkingTime')

                __changedDate = _changedDate.replace('T', ' ')

                if __changedDate > _last:
                    __full_time = _full_time if _full_time is not None else "null"
                    __workingTime = _workingTime if _workingTime is not None else "null"
                    __justification = f"'{_justification.encode('latin1').decode('unicode-escape')}'" if _justification is not None else "null"
                    db.execute(f"""INSERT INTO movidesk_status_histories 
                       (ticket_id, status, justification, changed_date, full_time, working_time) 
                        VALUES ({ticket_id}, '{_status}', {__justification}, '{__changedDate}', {__full_time},{__workingTime})""")

                print(f"{_i}({__changedDate > _last}): {_status}, {_justification}, {__changedDate}, {_full_time}, {_workingTime}, {ticket_id}")

        db.commit()                                                                         # comita no BD o que foi encontrado
    db.disconect()


def capturas_tickets_eq_interna():
    _i = 0
    _has_more = True
    while _has_more:
        tickets_eq_interna = movidesk.tickets_aguardando_eq_interna(_i)
        tickets = json.loads(tickets_eq_interna)
        _has_more = len(tickets) == 1000

        for ticket in tickets:
            _ticket_pai = ticket.get("id")
            _justificativa = ticket.get("justification")
            _assembla = ticket.get("customFieldValues")
            _ticket_filho = ticket.get("childrenTickets")
            _i += 1
            for assembla in _assembla:
                _id_assembla = assembla.get("value")
            for ticket_filho in _ticket_filho:
                _id_ticket_filho = ticket_filho.get("id")
            print(f"{_i}: {_ticket_pai}, {_justificativa}, {_id_assembla}, {_id_ticket_filho}")


if __name__ == '__main__':
    #create_tables()
    #capture_questions()
    #capture_responses(True)
    #capture_status_histories()
    capturas_tickets_eq_interna()
