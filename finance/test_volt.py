from copy import deepcopy
from decimal import Decimal
from io import BytesIO
from unittest.mock import Mock, patch
from urllib.error import URLError

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from .integrations import IntegrationUnavailable
from .volt import VoltAdapter, FashionService, post_json


def response():
    return {'conversation_id':'conversation-123', 'session_id':'conversation-123',
            'reply':'Opciones de Volt', 'products':[
                {'id':1,'name':'Camiseta','description':'Algodón','price':'39900.00','stock':30,'available_sizes':['S','M']},
                {'id':4,'name':'Camisa','description':'Franela','price':'89900.00','stock':18,'available_sizes':['L']},
            ]}


@override_settings(VOLT_BASE_URL='http://volt.example')
class VoltTests(TestCase):
    def test_contract_and_strict_price_filter(self):
        send=Mock(return_value=response())
        result=FashionService(VoltAdapter(send)).ask('Ropa casual',Decimal('50000'),'previous')
        self.assertEqual(len(result['products']),1)
        self.assertTrue(result['filtered'])
        send.assert_called_once_with('http://volt.example/api/chatbot/message/',
            {'message':'Ropa casual. Precio máximo de 50000.00 COP','conversation_id':'previous'})
        self.assertEqual(result['products'][0]['store_url'],'http://volt.example/#catalogo')

    def test_invalid_responses_are_rejected(self):
        cases=[None, {}, {'reply':42,'products':[]}, response()]
        cases[-1]['products'][0]['price']='NaN'
        for raw in cases:
            with self.assertRaises(IntegrationUnavailable): VoltAdapter(Mock(return_value=raw)).message('Hola')

    def test_empty_results_and_session_id_fallback(self):
        raw=response();raw.pop('conversation_id');raw['products']=[]
        result=VoltAdapter(Mock(return_value=raw)).message('Hola')
        self.assertEqual(result['products'],[])
        self.assertEqual(result['conversation_id'],'conversation-123')

    def test_zero_stock_is_hidden(self):
        raw=response();raw['products'][0]['stock']=0
        result=FashionService(VoltAdapter(Mock(return_value=raw))).ask('Hola')
        self.assertEqual([p['id'] for p in result['products']],[4])

    @override_settings(VOLT_BASE_URL='')
    def test_not_configured_does_not_call_network(self):
        send=Mock()
        with self.assertRaises(IntegrationUnavailable): VoltAdapter(send).message('Hola')
        send.assert_not_called()

    @patch('finance.volt.urlopen', side_effect=URLError('timeout'))
    def test_transport_failure_is_controlled(self, opener):
        with self.assertRaises(IntegrationUnavailable): post_json('http://volt.example/api/chatbot/message/',{'message':'Hola'})

    @patch('finance.volt.urlopen')
    def test_transport_uses_post_without_auth(self, opener):
        import json
        opener.return_value.__enter__.return_value=BytesIO(json.dumps(response()).encode())
        post_json('http://volt.example/api/chatbot/message/',{'message':'Hola','conversation_id':None})
        request=opener.call_args.args[0]
        self.assertEqual(request.get_method(),'POST')
        self.assertEqual(json.loads(request.data)['message'],'Hola')
        self.assertIsNone(request.get_header('Authorization'))

    @patch('finance.views.FrankfurterAdapter.rate', return_value={})
    @patch('finance.views.VoltAdapter')
    def test_conversation_form_reset_escaping_and_no_repost(self, adapter, rate):
        raw=response();raw['reply']='<script>alert(1)</script>'
        adapter.return_value.message.return_value=raw
        self.client.force_login(get_user_model().objects.create_user('volt-user'))
        first=self.client.post('/servicios/',{'message':'Camisa','max_price':'95000'},follow=True)
        self.assertContains(first,'&lt;script&gt;')
        self.assertNotContains(first,'<script>')
        self.assertEqual(adapter.return_value.message.call_args.args[1],None)
        self.client.get('/servicios/')
        self.assertEqual(adapter.return_value.message.call_count,1)
        self.client.post('/servicios/',{'message':'En rojo'})
        self.assertEqual(adapter.return_value.message.call_args.args[1],'conversation-123')
        self.client.post('/servicios/',{'action':'reset'})
        self.client.post('/servicios/',{'message':'Otra búsqueda'})
        self.assertEqual(adapter.return_value.message.call_args.args[1],None)
        self.client.logout()
        self.assertEqual(self.client.post('/servicios/',{'message':'Hola'}).status_code,302)

    @patch('finance.views.FrankfurterAdapter.rate', return_value={})
    @patch('finance.views.VoltAdapter')
    def test_invalid_form_never_calls_provider(self, adapter, rate):
        self.client.force_login(get_user_model().objects.create_user('invalid'))
        for data in [{'message':'a'*1001}, {'message':'Hola','max_price':'-1'}]:
            self.assertEqual(self.client.post('/servicios/',data).status_code,200)
        adapter.assert_not_called()
