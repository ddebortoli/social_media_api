from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Post, Comment
UserCredential = get_user_model()

class AuthenticatedAPITestCase(APITestCase):
    def setUp(self):
        self.auth_user = UserCredential.objects.create_user(username='authuser', password='authpassword')
        
        refresh = RefreshToken.for_user(self.auth_user)
        self.access_token = refresh.access_token

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

class UserTests(AuthenticatedAPITestCase):

    def test_create_social_user(self):
        self.authenticate()

        url = reverse('user-list')
        data = {'username': 'newuser', 'email': 'newuser@example.com'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_get_social_user_list(self):
        self.authenticate()

        User.objects.create(username='user1', email='user1@example.com')
        User.objects.create(username='user2', email='user2@example.com')

        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 2)

    def test_get_social_user_detail(self):
        self.authenticate()

        new_user = User.objects.create(username='newuser', email='newuser@example.com')
        url = reverse('user-detail', args=[new_user.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], 'newuser')

    def test_follow_user(self):
        self.authenticate()

        user_puca = User.objects.create(username='puca', email='puca@example.com')
        user_garu = User.objects.create(username='garu', email='garu@example.com')
        url = reverse('user-follow', args=[user_garu.id, user_puca.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user_garu.followers.filter(username='puca').exists())

class PostsTest(AuthenticatedAPITestCase):

    def test_create_post(self):
        self.authenticate()

        url = reverse('post-list')
        User.objects.create(username='user1', email='user1@example.com')
        data = {'author': 1, 'content': 'This is a testing post.'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='user1').exists())

    def test_get_posts(self):
        self.authenticate()

        new_user = User.objects.create(username='user1', email='user1@example.com')
        Post.objects.create(author=new_user, content='This is a testing post.')

        url = reverse('post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_get_post_by_id(self):
        self.authenticate()

        new_user = User.objects.create(username='user1', email='user1@example.com')
        new_post = Post.objects.create(author=new_user, content='This is a testing post.')

        url = reverse('post-detail', args=[new_post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_create_comment(self):
        self.authenticate()

        new_user = User.objects.create(username='user1', email='user1@example.com')
        new_post = Post.objects.create(author=new_user, content='This is a testing post.')

        url = reverse('comment-list', args=[new_post.id])
        data = {'author':new_user.id, 'content':'This is a testing comment from user1!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Post.objects.filter(author=new_user).exists())

        new_user_2 = User.objects.create(username='user2', email='user2@example.com')
        new_post_2 = Post.objects.create(author=new_user_2, content='This is a testing post.')

        url = reverse('comment-list', args=[new_post_2.id])
        data = {'author':new_user_2.id, 'content':'This is a testing comment from user2!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Post.objects.filter(author=new_user_2).exists())

    def test_get_comments(self):
        self.authenticate()

        new_user = User.objects.create(username='user1',email='user1@example.com')
        user_who_comment = User.objects.create(username='user_who_comments', email='user_who_comments@example.com')
        new_post = Post.objects.create(author=new_user, content='This is a testing post.')
        Comment.objects.create(post=new_post, author=user_who_comment, content='I am the one who comments!')

        url = reverse('comment-list', args=[new_post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertTrue(Comment.objects.filter(author=user_who_comment).exists())