import aiohttp
import hashlib
from datetime import datetime
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class WHMCSClient:
    def __init__(self):
        self.api_url = os.getenv("WHMCS_API_URL")
        self.identifier = os.getenv("WHMCS_IDENTIFIER")
        self.secret = os.getenv("WHMCS_SECRET")
        
    async def _make_request(self, action: str, params: Dict[str, Any]) -> Dict:
        """发送请求到WHMCS API"""
        params.update({
            'identifier': self.identifier,
            'secret': self.secret,
            'action': action,
            'responsetype': 'json',
        })
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, data=params) as response:
                return await response.json()
    
    async def create_client(self, email: str, password: str, firstname: str, 
                          lastname: str) -> Dict:
        """在WHMCS中创建客户"""
        params = {
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'password2': password,
        }
        return await self._make_request('AddClient', params)
    
    async def create_order(self, client_id: int, product_id: int, 
                         payment_method: str = "alipay") -> Dict:
        """在WHMCS中创建订单"""
        params = {
            'clientid': client_id,
            'pid': product_id,
            'paymentmethod': payment_method,
        }
        return await self._make_request('AddOrder', params)
    
    async def get_client_products(self, client_id: int) -> Dict:
        """获取客户的产品列表"""
        params = {
            'clientid': client_id,
            'stats': True,
        }
        return await self._make_request('GetClientsProducts', params)
    
    async def get_invoice(self, invoice_id: int) -> Dict:
        """获取发票详情"""
        params = {
            'invoiceid': invoice_id,
        }
        return await self._make_request('GetInvoice', params)
    
    async def create_invoice(self, client_id: int, items: list, 
                           due_date: Optional[str] = None) -> Dict:
        """创建发票"""
        if not due_date:
            due_date = datetime.now().strftime("%Y-%m-%d")
            
        params = {
            'userid': client_id,
            'date': datetime.now().strftime("%Y-%m-%d"),
            'duedate': due_date,
            'itemdescription[]': [item['description'] for item in items],
            'itemamount[]': [str(item['amount']) for item in items],
            'itemtaxed[]': [str(int(item.get('taxed', False))) for item in items],
        }
        return await self._make_request('CreateInvoice', params)
    
    async def get_products(self) -> Dict:
        """获取产品列表"""
        params = {}
        return await self._make_request('GetProducts', params)
    
    async def suspend_product(self, service_id: int, reason: str) -> Dict:
        """暂停产品/服务"""
        params = {
            'serviceid': service_id,
            'suspendreason': reason,
        }
        return await self._make_request('ModuleSuspend', params)
    
    async def unsuspend_product(self, service_id: int) -> Dict:
        """恢复产品/服务"""
        params = {
            'serviceid': service_id,
        }
        return await self._make_request('ModuleUnsuspend', params)
