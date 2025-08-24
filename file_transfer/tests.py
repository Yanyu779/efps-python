from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

# Create your tests here.

class AuthAndSessionTimeoutTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='tester', email='t@example.com', password='pass12345')
		self.dashboard_url = reverse('file_transfer:dashboard')
		self.login_url = reverse('file_transfer:custom_login')

	def test_redirects_unauthenticated_user_to_login(self):
		response = self.client.get(self.dashboard_url, follow=False)
		self.assertEqual(response.status_code, 302)
		self.assertTrue(self.login_url in response['Location'])

	def test_session_expires_after_5_minutes_inactivity(self):
		# 登录
		self.client.login(username='tester', password='pass12345')
		# 手动设置会话最后活动时间为6分钟前
		session = self.client.session
		expired_time = timezone.now() - datetime.timedelta(minutes=6)
		session['last_activity'] = expired_time.isoformat()
		session.save()

		# 访问受保护页面应被重定向到登录页
		response = self.client.get(self.dashboard_url, follow=False)
		self.assertEqual(response.status_code, 302)
		self.assertTrue(self.login_url in response['Location'])

		# 再次访问，确保确实已登出（会话被flush，is_authenticated为False）
		response2 = self.client.get(self.dashboard_url, follow=False)
		self.assertEqual(response2.status_code, 302)
		self.assertTrue(self.login_url in response2['Location'])
