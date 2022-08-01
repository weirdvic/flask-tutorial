import requests
from flask_babel import _
from flask import current_app

def translate(text:str, to_language:str) -> str:
    '''Перевести фрагмент текста '''
    if len(text) >= 10000:
        return _('Error: text is too long to translate.')
    if len(to_language) > 3:
        return _('Error: language code too long (max length 3)')

    if 'YANDEX_FOLDER_ID' not in current_app.config or \
        'YANDEX_TRANSLATE_KEY' not in current_app.config or \
        not current_app.config['YANDEX_FOLDER_ID'] or \
        not current_app.config['YANDEX_TRANSLATE_KEY']:
        return _('Error: the translation service is not configured.')
    folder_id = current_app.config.get('YANDEX_FOLDER_ID')
    api_key = current_app.config.get('YANDEX_TRANSLATE_KEY')

    body = {
        "targetLanguageCode": to_language,
        "texts": [text],
        "folderId": folder_id,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}"
    }

    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
        json=body,
        headers=headers,
        )
    if response.status_code != 200:
        return _('Error: the translation service failed.')
    return response.json().get('translations')[0].get('text')
