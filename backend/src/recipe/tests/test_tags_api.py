# """
# Tests for the Tags API.
# """
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .services import (
    create_tag_detail_url,
    TAG_LIST_URL,
    create_tag,
    create_user,
)
from ..models import Recipe, Tag
from ..serializers import TagSerializer


# ________
# GET /api/tags/:


class TagListTest(APITestCase, APIClient):
    """Tests GET the list of the tags"""

    def setUp(self):
        """Creates client, user and two tags records for the tests."""
        self.client = APIClient()

        self.user = create_user()
        self.client.force_authenticate(self.user)

        _ = create_tag(user=self.user)
        _ = create_tag(
            user=self.user,
            name="Test-tag2",
        )

    def test_list_tags_success(self):
        """Test list tags."""
        response = self.client.get(TAG_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tag_query = Tag.objects.all().order_by("-name")
        self.assertEqual(len(response.data), tag_query.count())

        serializer = TagSerializer(tag_query, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_list_tags_limited_access(self):
        """Test list tags for a specific user."""
        user2 = create_user(email="test2@example.com")
        self.client.force_authenticate(user2)
        _ = create_tag(user=user2)

        response = self.client.get(TAG_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tag_query = Tag.objects.filter(user=user2).order_by("-name")
        self.assertEqual(len(response.data), tag_query.count())

        serializer = TagSerializer(tag_query, many=True)
        self.assertEqual(response.data, serializer.data)


class TagListNotAuthenticatedAPITest(APITestCase, APIClient):
    """Tests calling endpoint with the unauthenticated user."""

    def setUp(self):
        """Creates client for the tests."""
        self.client = APIClient()

    def test_get_auth_required(self):
        """Test auth is required to call the get method on the tag-list endpoint."""
        response = self.client.get(TAG_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ________
# PUT,PATCH,DELETE /api/tags/{id}/:


class TagDetailedNotAuthenticatedAPITest(APITestCase, APIClient):
    """Tests calling endpoint with the unauthenticated user."""

    def setUp(self):
        """Creates client and tag for the tests."""
        self.client = APIClient()
        self.user = create_user()
        self.tag = create_tag(user=self.user)

    def test_put_auth_required(self):
        """
        Test auth is required to call the put method
        on the tag-detailed endpoint.
        """
        response = self.client.put(create_tag_detail_url(self.tag.id), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_auth_required(self):
        """
        Test auth is required to call the patch method
        on the tag-detailed endpoint.
        """
        response = self.client.patch(create_tag_detail_url(self.tag.id), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_auth_required(self):
        """
        Test auth is required to call the delete method
        on the tag-detailed endpoint.
        """
        response = self.client.delete(create_tag_detail_url(self.tag.id), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TagDetailedNotAuthorizedAPITest(APITestCase, APIClient):
    """Tests authorizations for authenticated user to call endpoint."""

    def setUp(self):
        """Creates client for the tests."""
        self.client = APIClient()
        self.user1 = create_user()
        self.user2 = create_user(email="test2@example.com")
        self.tag1 = create_tag(user=self.user1)
        self.tag2 = create_tag(user=self.user2)

    def test_put_have_no_permissions(self):
        """Test restricted access for an unauthorized user
        to call the put method on the tag-detailed endpoint."""
        self.client.force_authenticate(self.user1)
        response = self.client.put(create_tag_detail_url(self.tag2.id), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user2)
        response = self.client.put(create_tag_detail_url(self.tag1.id), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_have_no_permissions(self):
        """Test restricted access for an unauthorized user
        to call the patch method on the tag-detailed endpoint."""
        self.client.force_authenticate(self.user1)
        response = self.client.patch(create_tag_detail_url(self.tag2.id), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user2)
        response = self.client.patch(create_tag_detail_url(self.tag1.id), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_have_no_permissions(self):
        """Test restricted access for an unauthorized user
        to call the delete method on the tag-detailed endpoint."""
        self.client.force_authenticate(self.user1)
        response = self.client.delete(
            create_tag_detail_url(self.tag2.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(self.user2)
        response = self.client.delete(
            create_tag_detail_url(self.tag1.id), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateDetailedTest(APITestCase, APIClient):
    """Tests update detailed tag."""

    def setUp(self):
        """Creates client, user and tag record for the tests."""
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.tag = create_tag(user=self.user)

    def test_put_tag_detailed_success(self):
        """Test update(put) tag detailed."""
        payload = {"user": self.user, "name": "tag-name"}
        response = self.client.put(create_tag_detail_url(self.tag.id), payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tag.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(self.tag, key), value)

    def test_put_tag_detailed_error(self):
        """Test update(put) tag detailed."""
        payload = {"random": "data"}
        response = self.client.put(create_tag_detail_url(self.tag.id), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_tag_detailed_success(self):
        """Test update(patch) tag detailed."""
        payload = {"name": "tag-name-test"}
        response = self.client.patch(create_tag_detail_url(self.tag.id), payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.tag.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(self.tag, key), value)


class DeleteDetailedTest(APITestCase, APIClient):
    """Tests delete detailed tag."""

    def setUp(self):
        """Creates client, user and tag record for the tests."""
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.tag = create_tag(user=self.user)

    def test_delete_tag_detailed_success(self):
        """Test delete tag detailed."""
        response = self.client.delete(create_tag_detail_url(self.tag.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=self.tag.id).exists())

    def test_delete_tag_detailed_does_not_exist(self):
        """Test retrive tag detailed."""
        user2 = create_user(email="test2@test.com")
        tag = create_tag(user=user2)
        response = self.client.delete(create_tag_detail_url(tag.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Tag.objects.filter(id=tag.id).exists())
