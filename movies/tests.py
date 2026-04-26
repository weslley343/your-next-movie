import logging
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Movie

class MovieAPITests(APITestCase):
    def setUp(self):
        # Silencia avisos de requisições (400, 404) que são esperados nos testes de falha
        logging.getLogger('django.request').setLevel(logging.ERROR)
        
        # Create some initial movies for testing
        self.movie1 = Movie.objects.create(
            ranking=1,
            titulo="Movie One",
            generos="Action",
            data_lancamento="2024-01-01",
            duracao_minutos=120
        )
        self.movie2 = Movie.objects.create(
            ranking=2,
            titulo="Movie Two",
            generos="Drama",
            data_lancamento="2023-01-01",
            duracao_minutos=150
        )
        self.list_url = reverse('movie-list')
        self.detail_url = lambda pk: reverse('movie-detail', kwargs={'pk': pk})

    # --- SUCCESS TESTS ---

    def test_list_movies_no_auth(self):
        """Test listing movies without authentication (should succeed)"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be paginated
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_movies_by_genre(self):
        """Test filtering movies by genre"""
        response = self.client.get(self.list_url, {'generos': 'Action'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['titulo'], "Movie One")

    def test_search_movies_by_title(self):
        """Test searching movies by title"""
        response = self.client.get(self.list_url, {'search': 'Two'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['titulo'], "Movie Two")

    def test_create_movie_no_auth(self):
        """Test creating a movie without authentication (should succeed)"""
        data = {
            "titulo": "New Movie",
            "ranking": 3,
            "generos": "Comedy",
            "data_lancamento": "2024-05-01"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 3)

    def test_get_movie_detail(self):
        """Test getting a specific movie detail"""
        response = self.client.get(self.detail_url(self.movie1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], self.movie1.titulo)

    def test_update_movie(self):
        """Test updating a movie"""
        data = {"titulo": "Updated Title"}
        response = self.client.patch(self.detail_url(self.movie1.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.movie1.refresh_from_db()
        self.assertEqual(self.movie1.titulo, "Updated Title")

    def test_delete_movie(self):
        """Test deleting a movie"""
        response = self.client.delete(self.detail_url(self.movie1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Movie.objects.count(), 1)

    # --- FAILURE TESTS ---

    def test_create_movie_invalid_data(self):
        """Test creating a movie with invalid data (e.g. missing title)"""
        data = {"ranking": 10} # Missing required 'titulo'
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('titulo', response.data)

    def test_get_non_existent_movie(self):
        """Test getting a movie that doesn't exist"""
        response = self.client.get(self.detail_url(999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_non_existent_movie(self):
        """Test updating a movie that doesn't exist"""
        response = self.client.patch(self.detail_url(999), {"titulo": "Ghost"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existent_movie(self):
        """Test deleting a movie that doesn't exist"""
        response = self.client.delete(self.detail_url(999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AIInsightAPITests(APITestCase):
    def setUp(self):
        logging.getLogger('django.request').setLevel(logging.ERROR)
        from .models import AIInsight
        self.insight = AIInsight.objects.create(
            titulo="Tendências de 2024",
            introducao="Introdução estratégica",
            desenvolvimento="Conteúdo profundo sobre cinema...",
            conclusao="Conclusão estratégica."
        )
        self.list_url = reverse('ai-insight-list')
        self.detail_url = lambda pk: reverse('ai-insight-detail', kwargs={'pk': pk})

    def test_list_insights(self):
        """Testa a listagem de insights da IA"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_insight_detail(self):
        """Testa o detalhamento de um insight específico"""
        response = self.client.get(self.detail_url(self.insight.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], self.insight.titulo)

    def test_search_insights(self):
        """Testa a busca textual nos insights"""
        response = self.client.get(self.list_url, {'search': 'cinema'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_post_insight_not_allowed(self):
        """Garante que a criação manual de insights via API é proibida (405)"""
        data = {"titulo": "Tentativa", "desenvolvimento": "..."}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
