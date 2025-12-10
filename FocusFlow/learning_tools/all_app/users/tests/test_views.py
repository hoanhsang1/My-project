# all_app/users/tests/test_views.py - FIXED VERSION
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from unittest.mock import patch, MagicMock
from all_app.users.users_models import User
from all_app.users.users_form import login_form, register_form

# ==================== SHOW LOGIN TESTS ====================
class ShowLoginTest(TestCase):
    """Test show_login view - KHÔNG kế thừa"""
    
    def test_show_login_get(self):
        response = self.client.get(reverse('users:login_form'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/authenticate_page.html')
        self.assertIsInstance(response.context['form'], login_form)
        self.assertEqual(response.context['page'], 'login')
    
    def test_show_login_context(self):
        response = self.client.get(reverse('users:login_form'))
        
        self.assertIn('form', response.context)
        self.assertIn('page', response.context)
        self.assertEqual(response.context['page'], 'login')


# ==================== SHOW REGISTER TESTS ====================
class ShowRegisterTest(TestCase):
    """Test show_register view - KHÔNG kế thừa"""
    
    def test_show_register_get(self):
        response = self.client.get(reverse('users:register_form'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/authenticate_page.html')
        self.assertIsInstance(response.context['form'], register_form)
        self.assertEqual(response.context['page'], 'register')
    
    def test_show_register_context(self):
        response = self.client.get(reverse('users:register_form'))
        
        self.assertIn('form', response.context)
        self.assertIn('page', response.context)
        self.assertEqual(response.context['page'], 'register')


# ==================== CHECK LOGIN TESTS ====================
class CheckLoginTest(TestCase):
    """Test check_login view - có setUp riêng"""
    
    def setUp(self):
        self.client = Client()
        # Chỉ tạo user trong setUp của class này
        self.user = User.objects.create(
            username='testuser',
            password=make_password('testpass123'),
            email='test@example.com',
            fullname='Test User',
            role='user',
            is_deleted=False
        )
    
    def test_check_login_success_user(self):
        response = self.client.post(reverse('users:login_form-post'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('to_do_list:home'))
        
        session = self.client.session
        self.assertEqual(session['user_id'], str(self.user.user_id))
        self.assertEqual(session['role'], 'user')
    
    def test_check_login_success_admin(self):
        # Tạo admin user trong test method này
        admin_user = User.objects.create(
            username='adminuser',
            password=make_password('adminpass123'),
            email='admin@example.com',
            fullname='Admin User',
            role='admin',
            is_deleted=False
        )
        
        response = self.client.post(reverse('users:login_form-post'), {
            'username': 'adminuser',
            'password': 'adminpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_manage:admin_manage_dashboard'))
    
    def test_check_login_wrong_password(self):
        response = self.client.post(reverse('users:login_form-post'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/authenticate_page.html')
        self.assertContains(response, 'Mật khẩu không đúng')
    
    def test_check_login_user_not_exist(self):
        response = self.client.post(reverse('users:login_form-post'), {
            'username': 'nonexistent',
            'password': 'anypassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/authenticate_page.html')
        self.assertContains(response, 'Tên đăng nhập không tồn tại hoặc đã bị xóa')
    
    def test_check_login_deleted_user(self):
        # Tạo user bị xóa trong test method này
        deleted_user = User.objects.create(
            username='deleteduser',
            password=make_password('password123'),
            email='deleted@example.com',
            fullname='Deleted User',
            role='user',
            is_deleted=True
        )
        
        response = self.client.post(reverse('users:login_form-post'), {
            'username': 'deleteduser',
            'password': 'password123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/authenticate_page.html')
        self.assertContains(response, 'Tên đăng nhập không tồn tại hoặc đã bị xóa')
    
    def test_check_login_get_request(self):
        response = self.client.get(reverse('users:login_form-post'))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:login'))


# ==================== REGISTER USER TESTS ====================
class RegisterUserTest(TestCase):
    """Test register_user view - có setUp riêng"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register_form-post')
        
        # Dữ liệu đăng ký hợp lệ
        self.valid_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'fullname': 'New User',
            'password': 'StrongPass123',
            'confirm_password': 'StrongPass123'
        }
        
        # KHÔNG tạo user ở đây - sẽ tạo trong mỗi test method nếu cần
    
    def test_register_user_success(self):
        """Test đăng ký thành công - KHÔNG có existing_user trong setUp"""
        response = self.client.post(self.register_url, self.valid_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('to_do_list:home'))
        
        # Kiểm tra user được tạo
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.fullname, 'New User')
        self.assertEqual(user.role, 'user')
        self.assertFalse(user.is_deleted)
        
        # Kiểm tra password được hash
        self.assertTrue(check_password('StrongPass123', user.password))
        
        # Kiểm tra session
        session = self.client.session
        self.assertEqual(session['user_id'], str(user.user_id))
        self.assertEqual(session['role'], 'user')
    
    def test_register_user_duplicate_username(self):
        """Test đăng ký với username đã tồn tại"""
        # Tạo user trước trong test method này
        User.objects.create(
            username='existinguser',
            email='existing@example.com',
            password=make_password('password123'),
            fullname='Existing User',
            role='user',
            is_deleted=False
        )
        
        data = self.valid_data.copy()
        data['username'] = 'existinguser'
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/authenticate_page.html')
        self.assertContains(response, 'Tên đăng nhập đã tồn tại')
    
    def test_register_user_duplicate_email(self):
        """Test đăng ký với email đã tồn tại"""
        # Tạo user trước trong test method này
        User.objects.create(
            username='existinguser',
            email='existing@example.com',
            password=make_password('password123'),
            fullname='Existing User',
            role='user',
            is_deleted=False
        )
        
        data = self.valid_data.copy()
        data['email'] = 'existing@example.com'
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/authenticate_page.html')
        self.assertContains(response, 'Email đã tồn tại')
    
    def test_register_user_invalid_form(self):
        """Test đăng ký với form không hợp lệ"""
        data = self.valid_data.copy()
        data['password'] = '123'
        data['confirm_password'] = '123'
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/authenticate_page.html')
        self.assertTrue('form' in response.context)
        
        form = response.context['form']
        self.assertTrue(form.errors)
    
    def test_register_user_password_mismatch(self):
        """Test password và confirm_password không khớp"""
        data = self.valid_data.copy()
        data['confirm_password'] = 'DifferentPassword123'
        
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/authenticate_page.html')
        
        form = response.context['form']
        self.assertIn('confirm_password', form.errors)
    
    def test_register_user_get_request(self):
        """Test GET request đến register_user"""
        response = self.client.get(self.register_url)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:login'))
    
    @patch('all_app.users.views.ToDoList')
    @patch('all_app.users.views.Flashcard')
    @patch('all_app.users.views.Habit')
    @patch('all_app.users.views.Pomodoro')
    @patch('all_app.users.views.Calendar')
    def test_register_user_creates_related_objects(self, mock_calendar, mock_pomodoro, 
                                                  mock_habit, mock_flashcard, mock_todo):
        """Test tạo các đối tượng liên quan khi đăng ký - Mock để không cần database"""
        # Mock các model
        mock_todo_instance = MagicMock()
        mock_todo.objects.create.return_value = mock_todo_instance
        
        mock_flashcard_instance = MagicMock()
        mock_flashcard.objects.create.return_value = mock_flashcard_instance
        
        mock_habit_instance = MagicMock()
        mock_habit.objects.create.return_value = mock_habit_instance
        
        mock_pomodoro_instance = MagicMock()
        mock_pomodoro.objects.create.return_value = mock_pomodoro_instance
        
        mock_calendar_instance = MagicMock()
        mock_calendar.objects.create.return_value = mock_calendar_instance
        
        response = self.client.post(self.register_url, self.valid_data)
        
        # Với mock, chúng ta không cần kiểm tra database
        self.assertEqual(response.status_code, 302)
        
        # Kiểm tra các phương thức create được gọi
        # Vì mock, chúng ta không thể lấy user từ database
        # Nhưng có thể kiểm tra mock được gọi
        mock_todo.objects.create.assert_called_once()
        mock_flashcard.objects.create.assert_called_once()
        mock_habit.objects.create.assert_called_once()
        mock_pomodoro.objects.create.assert_called_once()
        mock_calendar.objects.create.assert_called_once()