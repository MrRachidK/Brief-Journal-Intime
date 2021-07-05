from src.utils.classes import Text
import urllib.request
import src.utils.api as script

def test_http_return(monkeypatch):
    text : Text
    results = [{
            "id_customer": 1,
            "text_date": "2021-06-30",
            "text": "I am happy"
          }
        ]

    def mockreturn(request):
        return results

    monkeypatch.setattr(urllib.request, 'urlopen', mockreturn)
    assert script.create_text(text) == results